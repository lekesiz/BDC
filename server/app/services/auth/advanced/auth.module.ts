import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { EventEmitterModule } from '@nestjs/event-emitter';
import { MFAService } from './mfa.service';
import { SSOService } from './sso.service';
import { BiometricService } from './biometric.service';
import { SessionService } from './session.service';
import { AuthFlowService } from './auth-flow.service';

@Module({
  imports: [
    ConfigModule,
    EventEmitterModule.forRoot(),
    JwtModule.registerAsync({
      imports: [ConfigModule],
      useFactory: async (configService: ConfigService) => ({
        global: true,
        secret: configService.get('JWT_ACCESS_SECRET'),
        signOptions: {
          expiresIn: '15m',
        },
      }),
      inject: [ConfigService],
    }),
  ],
  providers: [
    MFAService,
    SSOService,
    BiometricService,
    SessionService,
    AuthFlowService,
  ],
  exports: [
    MFAService,
    SSOService,
    BiometricService,
    SessionService,
    AuthFlowService,
  ],
})
export class AdvancedAuthModule {}