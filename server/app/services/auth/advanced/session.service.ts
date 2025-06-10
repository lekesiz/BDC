import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { Redis } from 'ioredis';
import { randomBytes } from 'crypto';
import { Request } from 'express';
import * as geoip from 'geoip-lite';
import * as useragent from 'useragent';

export interface Session {
  id: string;
  userId: string;
  deviceId: string;
  ipAddress: string;
  userAgent: string;
  location?: {
    country: string;
    region: string;
    city: string;
    latitude: number;
    longitude: number;
  };
  device?: {
    browser: string;
    os: string;
    device: string;
  };
  createdAt: Date;
  lastActivityAt: Date;
  expiresAt: Date;
  refreshToken?: string;
  mfaVerified: boolean;
  elevatedUntil?: Date;
  metadata?: Record<string, any>;
}

export interface SessionToken {
  sessionId: string;
  userId: string;
  deviceId: string;
  type: 'access' | 'refresh';
}

export interface SessionActivity {
  sessionId: string;
  action: string;
  ipAddress: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

@Injectable()
export class SessionService {
  private redis: Redis;
  private readonly sessionPrefix = 'session:';
  private readonly userSessionsPrefix = 'user:sessions:';
  private readonly devicePrefix = 'device:';
  private readonly activityPrefix = 'activity:';

  constructor(
    private configService: ConfigService,
    private jwtService: JwtService
  ) {
    this.redis = new Redis({
      host: this.configService.get('REDIS_HOST'),
      port: this.configService.get('REDIS_PORT'),
      password: this.configService.get('REDIS_PASSWORD'),
      db: 1, // Use separate DB for sessions
    });
  }

  /**
   * Create a new session
   */
  async createSession(
    userId: string,
    request: Request,
    options?: {
      rememberMe?: boolean;
      mfaVerified?: boolean;
      metadata?: Record<string, any>;
    }
  ): Promise<{
    session: Session;
    accessToken: string;
    refreshToken: string;
  }> {
    const sessionId = this.generateSessionId();
    const deviceId = await this.getOrCreateDeviceId(request);
    
    // Extract session information
    const ipAddress = this.getClientIp(request);
    const userAgentString = request.headers['user-agent'] || '';
    const location = this.getLocationFromIp(ipAddress);
    const device = this.parseUserAgent(userAgentString);

    // Set session duration based on remember me option
    const sessionDuration = options?.rememberMe
      ? 30 * 24 * 60 * 60 * 1000 // 30 days
      : 24 * 60 * 60 * 1000; // 24 hours

    const now = new Date();
    const expiresAt = new Date(now.getTime() + sessionDuration);

    const session: Session = {
      id: sessionId,
      userId,
      deviceId,
      ipAddress,
      userAgent: userAgentString,
      location,
      device,
      createdAt: now,
      lastActivityAt: now,
      expiresAt,
      mfaVerified: options?.mfaVerified || false,
      metadata: options?.metadata,
    };

    // Generate tokens
    const accessToken = await this.generateAccessToken(sessionId, userId, deviceId);
    const refreshToken = await this.generateRefreshToken(sessionId, userId, deviceId);
    
    session.refreshToken = refreshToken;

    // Store session in Redis
    await this.storeSession(session);
    
    // Add session to user's session list
    await this.addUserSession(userId, sessionId);
    
    // Record session creation activity
    await this.recordActivity(sessionId, 'session_created', ipAddress);

    // Check for suspicious activity
    await this.checkSuspiciousActivity(userId, ipAddress, deviceId);

    return {
      session,
      accessToken,
      refreshToken,
    };
  }

  /**
   * Get session by ID
   */
  async getSession(sessionId: string): Promise<Session | null> {
    const data = await this.redis.get(`${this.sessionPrefix}${sessionId}`);
    
    if (!data) {
      return null;
    }

    const session = JSON.parse(data) as Session;
    
    // Check if session is expired
    if (new Date() > new Date(session.expiresAt)) {
      await this.terminateSession(sessionId);
      return null;
    }

    return session;
  }

  /**
   * Update session activity
   */
  async updateSessionActivity(
    sessionId: string,
    ipAddress?: string
  ): Promise<void> {
    const session = await this.getSession(sessionId);
    
    if (!session) {
      return;
    }

    session.lastActivityAt = new Date();
    
    // Update location if IP changed
    if (ipAddress && ipAddress !== session.ipAddress) {
      session.ipAddress = ipAddress;
      session.location = this.getLocationFromIp(ipAddress);
      
      // Record IP change
      await this.recordActivity(sessionId, 'ip_changed', ipAddress, {
        oldIp: session.ipAddress,
        newIp: ipAddress,
      });
    }

    await this.storeSession(session);
  }

  /**
   * Terminate a session
   */
  async terminateSession(sessionId: string): Promise<void> {
    const session = await this.getSession(sessionId);
    
    if (!session) {
      return;
    }

    // Remove session from Redis
    await this.redis.del(`${this.sessionPrefix}${sessionId}`);
    
    // Remove from user's session list
    await this.redis.srem(`${this.userSessionsPrefix}${session.userId}`, sessionId);
    
    // Record termination
    await this.recordActivity(sessionId, 'session_terminated', session.ipAddress);
  }

  /**
   * Terminate all sessions for a user
   */
  async terminateAllUserSessions(
    userId: string,
    exceptSessionId?: string
  ): Promise<void> {
    const sessionIds = await this.getUserSessions(userId);
    
    for (const sessionId of sessionIds) {
      if (sessionId !== exceptSessionId) {
        await this.terminateSession(sessionId);
      }
    }
  }

  /**
   * Get all active sessions for a user
   */
  async getUserSessions(userId: string): Promise<string[]> {
    const sessionIds = await this.redis.smembers(
      `${this.userSessionsPrefix}${userId}`
    );
    
    return sessionIds;
  }

  /**
   * Get detailed session information for a user
   */
  async getUserSessionDetails(userId: string): Promise<Session[]> {
    const sessionIds = await this.getUserSessions(userId);
    const sessions: Session[] = [];
    
    for (const sessionId of sessionIds) {
      const session = await this.getSession(sessionId);
      if (session) {
        sessions.push(session);
      }
    }
    
    // Sort by last activity
    sessions.sort((a, b) => 
      new Date(b.lastActivityAt).getTime() - new Date(a.lastActivityAt).getTime()
    );
    
    return sessions;
  }

  /**
   * Verify and refresh access token
   */
  async refreshAccessToken(refreshToken: string): Promise<{
    accessToken: string;
    refreshToken: string;
  } | null> {
    try {
      const payload = await this.jwtService.verifyAsync<SessionToken>(
        refreshToken,
        {
          secret: this.configService.get('JWT_REFRESH_SECRET'),
        }
      );

      if (payload.type !== 'refresh') {
        return null;
      }

      const session = await this.getSession(payload.sessionId);
      
      if (!session || session.refreshToken !== refreshToken) {
        return null;
      }

      // Generate new tokens
      const accessToken = await this.generateAccessToken(
        payload.sessionId,
        payload.userId,
        payload.deviceId
      );
      
      const newRefreshToken = await this.generateRefreshToken(
        payload.sessionId,
        payload.userId,
        payload.deviceId
      );

      // Update session with new refresh token
      session.refreshToken = newRefreshToken;
      await this.storeSession(session);

      return {
        accessToken,
        refreshToken: newRefreshToken,
      };
    } catch {
      return null;
    }
  }

  /**
   * Elevate session privileges (for sensitive operations)
   */
  async elevateSession(
    sessionId: string,
    duration: number = 15 * 60 * 1000 // 15 minutes
  ): Promise<void> {
    const session = await this.getSession(sessionId);
    
    if (!session) {
      throw new Error('Session not found');
    }

    session.elevatedUntil = new Date(Date.now() + duration);
    await this.storeSession(session);
    
    await this.recordActivity(sessionId, 'session_elevated', session.ipAddress);
  }

  /**
   * Check if session has elevated privileges
   */
  async isSessionElevated(sessionId: string): Promise<boolean> {
    const session = await this.getSession(sessionId);
    
    if (!session || !session.elevatedUntil) {
      return false;
    }

    return new Date() < new Date(session.elevatedUntil);
  }

  /**
   * Store session in Redis
   */
  private async storeSession(session: Session): Promise<void> {
    const ttl = Math.floor(
      (new Date(session.expiresAt).getTime() - Date.now()) / 1000
    );
    
    await this.redis.setex(
      `${this.sessionPrefix}${session.id}`,
      ttl,
      JSON.stringify(session)
    );
  }

  /**
   * Add session to user's session list
   */
  private async addUserSession(userId: string, sessionId: string): Promise<void> {
    await this.redis.sadd(`${this.userSessionsPrefix}${userId}`, sessionId);
  }

  /**
   * Generate session ID
   */
  private generateSessionId(): string {
    return randomBytes(32).toString('hex');
  }

  /**
   * Get or create device ID
   */
  private async getOrCreateDeviceId(request: Request): Promise<string> {
    const deviceFingerprint = this.generateDeviceFingerprint(request);
    let deviceId = await this.redis.get(`${this.devicePrefix}${deviceFingerprint}`);
    
    if (!deviceId) {
      deviceId = randomBytes(16).toString('hex');
      await this.redis.setex(
        `${this.devicePrefix}${deviceFingerprint}`,
        365 * 24 * 60 * 60, // 1 year
        deviceId
      );
    }
    
    return deviceId;
  }

  /**
   * Generate device fingerprint
   */
  private generateDeviceFingerprint(request: Request): string {
    const userAgent = request.headers['user-agent'] || '';
    const acceptLanguage = request.headers['accept-language'] || '';
    const acceptEncoding = request.headers['accept-encoding'] || '';
    
    return Buffer.from(
      `${userAgent}|${acceptLanguage}|${acceptEncoding}`
    ).toString('base64');
  }

  /**
   * Generate access token
   */
  private async generateAccessToken(
    sessionId: string,
    userId: string,
    deviceId: string
  ): Promise<string> {
    const payload: SessionToken = {
      sessionId,
      userId,
      deviceId,
      type: 'access',
    };

    return this.jwtService.signAsync(payload, {
      secret: this.configService.get('JWT_ACCESS_SECRET'),
      expiresIn: '15m',
    });
  }

  /**
   * Generate refresh token
   */
  private async generateRefreshToken(
    sessionId: string,
    userId: string,
    deviceId: string
  ): Promise<string> {
    const payload: SessionToken = {
      sessionId,
      userId,
      deviceId,
      type: 'refresh',
    };

    return this.jwtService.signAsync(payload, {
      secret: this.configService.get('JWT_REFRESH_SECRET'),
      expiresIn: '30d',
    });
  }

  /**
   * Get client IP address
   */
  private getClientIp(request: Request): string {
    const forwarded = request.headers['x-forwarded-for'];
    
    if (forwarded) {
      return (forwarded as string).split(',')[0].trim();
    }
    
    return request.ip || request.connection.remoteAddress || '';
  }

  /**
   * Get location from IP address
   */
  private getLocationFromIp(ipAddress: string): Session['location'] {
    const geo = geoip.lookup(ipAddress);
    
    if (!geo) {
      return undefined;
    }

    return {
      country: geo.country,
      region: geo.region,
      city: geo.city,
      latitude: geo.ll[0],
      longitude: geo.ll[1],
    };
  }

  /**
   * Parse user agent string
   */
  private parseUserAgent(userAgentString: string): Session['device'] {
    const agent = useragent.parse(userAgentString);
    
    return {
      browser: agent.toAgent(),
      os: agent.os.toString(),
      device: agent.device.toString(),
    };
  }

  /**
   * Record session activity
   */
  private async recordActivity(
    sessionId: string,
    action: string,
    ipAddress: string,
    metadata?: Record<string, any>
  ): Promise<void> {
    const activity: SessionActivity = {
      sessionId,
      action,
      ipAddress,
      timestamp: new Date(),
      metadata,
    };

    // Store activity with TTL
    await this.redis.zadd(
      `${this.activityPrefix}${sessionId}`,
      Date.now(),
      JSON.stringify(activity)
    );

    // Keep only last 100 activities
    await this.redis.zremrangebyrank(
      `${this.activityPrefix}${sessionId}`,
      0,
      -101
    );
  }

  /**
   * Check for suspicious activity
   */
  private async checkSuspiciousActivity(
    userId: string,
    ipAddress: string,
    deviceId: string
  ): Promise<void> {
    // Get user's recent sessions
    const sessions = await this.getUserSessionDetails(userId);
    
    // Check for multiple locations
    const locations = new Set(
      sessions
        .map(s => s.location?.country)
        .filter(Boolean)
    );
    
    if (locations.size > 3) {
      // Alert: User accessing from multiple countries
      console.warn(`Suspicious activity: User ${userId} accessing from ${locations.size} countries`);
    }

    // Check for new device
    const knownDevices = new Set(sessions.map(s => s.deviceId));
    if (!knownDevices.has(deviceId)) {
      // Alert: New device detected
      console.warn(`New device detected for user ${userId}`);
    }
  }

  /**
   * Get session activity history
   */
  async getSessionActivity(
    sessionId: string,
    limit: number = 50
  ): Promise<SessionActivity[]> {
    const activities = await this.redis.zrevrange(
      `${this.activityPrefix}${sessionId}`,
      0,
      limit - 1
    );

    return activities.map(data => JSON.parse(data) as SessionActivity);
  }
}