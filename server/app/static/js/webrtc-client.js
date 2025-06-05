/**
 * WebRTC Client for Video Conference Integration
 * Provides peer-to-peer video calling functionality
 */

class WebRTCClient {
    constructor(config = {}) {
        this.config = {
            iceServers: config.iceServers || [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ],
            socketUrl: config.socketUrl || 'ws://localhost:5000',
            autoJoinRoom: config.autoJoinRoom !== false,
            enableAudio: config.enableAudio !== false,
            enableVideo: config.enableVideo !== false,
            enableChat: config.enableChat !== false,
            enableScreenShare: config.enableScreenShare !== false,
            debug: config.debug || false
        };
        
        this.localStream = null;
        this.localVideo = null;
        this.remoteVideos = new Map();
        this.peerConnections = new Map();
        this.dataChannels = new Map();
        this.socket = null;
        
        this.roomId = null;
        this.participantId = null;
        this.userId = null;
        this.isHost = false;
        this.isRecording = false;
        this.isScreenSharing = false;
        
        // Event handlers
        this.onParticipantJoined = null;
        this.onParticipantLeft = null;
        this.onChatMessage = null;
        this.onRecordingStarted = null;
        this.onRecordingStopped = null;
        this.onScreenShareStarted = null;
        this.onScreenShareStopped = null;
        this.onError = null;
        
        this._log('WebRTC Client initialized', this.config);
    }
    
    /**
     * Initialize and join a WebRTC room
     */
    async joinRoom(roomId, userId) {
        try {
            this.roomId = roomId;
            this.userId = userId;
            
            this._log(`Joining room ${roomId} as user ${userId}`);
            
            // Initialize socket connection
            await this._initializeSocket();
            
            // Get user media
            if (this.config.autoJoinRoom) {
                await this._getUserMedia();
            }
            
            // Join the room via socket
            this.socket.emit('webrtc_join_room', {
                room_id: roomId,
                user_id: userId
            });
            
        } catch (error) {
            this._handleError('Failed to join room', error);
        }
    }
    
    /**
     * Leave the WebRTC room
     */
    leaveRoom() {
        try {
            this._log('Leaving room');
            
            // Close all peer connections
            this.peerConnections.forEach((pc, participantId) => {
                pc.close();
            });
            this.peerConnections.clear();
            
            // Close data channels
            this.dataChannels.forEach((channel) => {
                channel.close();
            });
            this.dataChannels.clear();
            
            // Stop local stream
            if (this.localStream) {
                this.localStream.getTracks().forEach(track => track.stop());
                this.localStream = null;
            }
            
            // Clear remote videos
            this.remoteVideos.clear();
            
            // Close socket
            if (this.socket) {
                this.socket.disconnect();
                this.socket = null;
            }
            
        } catch (error) {
            this._handleError('Error leaving room', error);
        }
    }
    
    /**
     * Send chat message
     */
    sendChatMessage(message) {
        if (!this.socket || !message.trim()) return;
        
        this.socket.emit('webrtc_chat_message', {
            message: message.trim()
        });
    }
    
    /**
     * Toggle audio mute
     */
    toggleAudio() {
        if (!this.localStream) return false;
        
        const audioTrack = this.localStream.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = !audioTrack.enabled;
            this._broadcastMediaState();
            return !audioTrack.enabled; // Return muted state
        }
        return false;
    }
    
    /**
     * Toggle video mute
     */
    toggleVideo() {
        if (!this.localStream) return false;
        
        const videoTrack = this.localStream.getVideoTracks()[0];
        if (videoTrack) {
            videoTrack.enabled = !videoTrack.enabled;
            this._broadcastMediaState();
            return !videoTrack.enabled; // Return muted state
        }
        return false;
    }
    
    /**
     * Start screen sharing
     */
    async startScreenShare() {
        try {
            if (this.isScreenSharing) return;
            
            const screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: true,
                audio: true
            });
            
            // Replace video track in all peer connections
            const videoTrack = screenStream.getVideoTracks()[0];
            this.peerConnections.forEach(async (pc) => {
                const sender = pc.getSenders().find(s => 
                    s.track && s.track.kind === 'video'
                );
                if (sender) {
                    await sender.replaceTrack(videoTrack);
                }
            });
            
            // Update local video
            if (this.localVideo) {
                this.localVideo.srcObject = screenStream;
            }
            
            this.isScreenSharing = true;
            
            // Handle screen share ending
            videoTrack.onended = () => {
                this.stopScreenShare();
            };
            
            // Notify other participants
            this.socket.emit('webrtc_signal', {
                type: 'screen_share_start'
            });
            
            this._log('Screen sharing started');
            
        } catch (error) {
            this._handleError('Failed to start screen sharing', error);
        }
    }
    
    /**
     * Stop screen sharing
     */
    async stopScreenShare() {
        try {
            if (!this.isScreenSharing) return;
            
            // Get camera stream back
            const cameraStream = await navigator.mediaDevices.getUserMedia({
                video: this.config.enableVideo,
                audio: false // Don't replace audio
            });
            
            // Replace video track in all peer connections
            const videoTrack = cameraStream.getVideoTracks()[0];
            this.peerConnections.forEach(async (pc) => {
                const sender = pc.getSenders().find(s => 
                    s.track && s.track.kind === 'video'
                );
                if (sender) {
                    await sender.replaceTrack(videoTrack);
                }
            });
            
            // Update local video
            if (this.localVideo) {
                const audioTrack = this.localStream.getAudioTracks()[0];
                this.localStream = new MediaStream([videoTrack]);
                if (audioTrack) {
                    this.localStream.addTrack(audioTrack);
                }
                this.localVideo.srcObject = this.localStream;
            }
            
            this.isScreenSharing = false;
            
            // Notify other participants
            this.socket.emit('webrtc_signal', {
                type: 'screen_share_stop'
            });
            
            this._log('Screen sharing stopped');
            
        } catch (error) {
            this._handleError('Failed to stop screen sharing', error);
        }
    }
    
    /**
     * Start recording (if host)
     */
    startRecording() {
        if (!this.isHost) {
            this._handleError('Only host can start recording');
            return;
        }
        
        this.socket.emit('webrtc_start_recording');
    }
    
    /**
     * Stop recording (if host)
     */
    stopRecording() {
        if (!this.isHost) {
            this._handleError('Only host can stop recording');
            return;
        }
        
        this.socket.emit('webrtc_stop_recording');
    }
    
    /**
     * Set local video element
     */
    setLocalVideo(videoElement) {
        this.localVideo = videoElement;
        if (this.localStream) {
            videoElement.srcObject = this.localStream;
        }
    }
    
    /**
     * Add remote video element for participant
     */
    addRemoteVideo(participantId, videoElement) {
        this.remoteVideos.set(participantId, videoElement);
    }
    
    /**
     * Remove remote video element for participant
     */
    removeRemoteVideo(participantId) {
        this.remoteVideos.delete(participantId);
    }
    
    /**
     * Get current media state
     */
    getMediaState() {
        const audioTrack = this.localStream?.getAudioTracks()[0];
        const videoTrack = this.localStream?.getVideoTracks()[0];
        
        return {
            isAudioMuted: !audioTrack?.enabled,
            isVideoMuted: !videoTrack?.enabled,
            isScreenSharing: this.isScreenSharing,
            isRecording: this.isRecording
        };
    }
    
    // Private methods
    
    async _initializeSocket() {
        return new Promise((resolve, reject) => {
            this.socket = io(this.config.socketUrl);
            
            this.socket.on('connect', () => {
                this._log('Socket connected');
                resolve();
            });
            
            this.socket.on('disconnect', () => {
                this._log('Socket disconnected');
            });
            
            this.socket.on('webrtc_joined', (data) => {
                this._handleRoomJoined(data);
            });
            
            this.socket.on('webrtc_participant_joined', (data) => {
                this._handleParticipantJoined(data);
            });
            
            this.socket.on('webrtc_participant_left', (data) => {
                this._handleParticipantLeft(data);
            });
            
            this.socket.on('webrtc_signal', (data) => {
                this._handleSignal(data);
            });
            
            this.socket.on('webrtc_event', (data) => {
                this._handleEvent(data);
            });
            
            this.socket.on('webrtc_error', (data) => {
                this._handleError('WebRTC error', data.error);
            });
            
            this.socket.on('connect_error', (error) => {
                reject(error);
            });
        });
    }
    
    async _getUserMedia() {
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia({
                video: this.config.enableVideo,
                audio: this.config.enableAudio
            });
            
            if (this.localVideo) {
                this.localVideo.srcObject = this.localStream;
            }
            
            this._log('Got user media');
            
        } catch (error) {
            this._handleError('Failed to get user media', error);
        }
    }
    
    async _createPeerConnection(participantId) {
        const pc = new RTCPeerConnection({
            iceServers: this.config.iceServers
        });
        
        this.peerConnections.set(participantId, pc);
        
        // Add local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => {
                pc.addTrack(track, this.localStream);
            });
        }
        
        // Handle remote stream
        pc.ontrack = (event) => {
            const remoteVideo = this.remoteVideos.get(participantId);
            if (remoteVideo) {
                remoteVideo.srcObject = event.streams[0];
            }
        };
        
        // Handle ICE candidates
        pc.onicecandidate = (event) => {
            if (event.candidate) {
                this.socket.emit('webrtc_signal', {
                    type: 'ice_candidate',
                    candidate: event.candidate,
                    target_participant: participantId
                });
            }
        };
        
        // Create data channel for chat
        if (this.config.enableChat) {
            const dataChannel = pc.createDataChannel('chat');
            this._setupDataChannel(dataChannel, participantId);
        }
        
        // Handle incoming data channels
        pc.ondatachannel = (event) => {
            this._setupDataChannel(event.channel, participantId);
        };
        
        return pc;
    }
    
    _setupDataChannel(channel, participantId) {
        this.dataChannels.set(participantId, channel);
        
        channel.onopen = () => {
            this._log(`Data channel opened with ${participantId}`);
        };
        
        channel.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                if (this.onChatMessage) {
                    this.onChatMessage(message);
                }
            } catch (error) {
                this._log('Invalid chat message received', error);
            }
        };
    }
    
    async _handleRoomJoined(data) {
        this.participantId = data.participant_id;
        this.isHost = data.is_host;
        
        this._log('Joined room successfully', data);
        
        // Create peer connections for existing participants
        for (const participant of data.participants) {
            if (participant.participant_id !== this.participantId) {
                await this._createPeerConnection(participant.participant_id);
            }
        }
    }
    
    async _handleParticipantJoined(data) {
        this._log('Participant joined', data);
        
        if (data.participant_id !== this.participantId) {
            // Create peer connection and send offer
            const pc = await this._createPeerConnection(data.participant_id);
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            
            this.socket.emit('webrtc_signal', {
                type: 'offer',
                offer: offer,
                target_participant: data.participant_id
            });
        }
        
        if (this.onParticipantJoined) {
            this.onParticipantJoined(data);
        }
    }
    
    _handleParticipantLeft(data) {
        this._log('Participant left', data);
        
        // Clean up peer connection
        const pc = this.peerConnections.get(data.participant_id);
        if (pc) {
            pc.close();
            this.peerConnections.delete(data.participant_id);
        }
        
        // Clean up data channel
        const channel = this.dataChannels.get(data.participant_id);
        if (channel) {
            channel.close();
            this.dataChannels.delete(data.participant_id);
        }
        
        // Clear remote video
        const remoteVideo = this.remoteVideos.get(data.participant_id);
        if (remoteVideo) {
            remoteVideo.srcObject = null;
        }
        
        if (this.onParticipantLeft) {
            this.onParticipantLeft(data);
        }
    }
    
    async _handleSignal(data) {
        const pc = this.peerConnections.get(data.from_participant);
        if (!pc) return;
        
        try {
            switch (data.type) {
                case 'offer':
                    await pc.setRemoteDescription(data.offer);
                    const answer = await pc.createAnswer();
                    await pc.setLocalDescription(answer);
                    
                    this.socket.emit('webrtc_signal', {
                        type: 'answer',
                        answer: answer,
                        target_participant: data.from_participant
                    });
                    break;
                    
                case 'answer':
                    await pc.setRemoteDescription(data.answer);
                    break;
                    
                case 'ice_candidate':
                    await pc.addIceCandidate(data.candidate);
                    break;
            }
        } catch (error) {
            this._handleError('Error handling signal', error);
        }
    }
    
    _handleEvent(data) {
        switch (data.type) {
            case 'chat_message':
                if (this.onChatMessage) {
                    this.onChatMessage(data.message);
                }
                break;
                
            case 'recording_started':
                this.isRecording = true;
                if (this.onRecordingStarted) {
                    this.onRecordingStarted(data);
                }
                break;
                
            case 'recording_stopped':
                this.isRecording = false;
                if (this.onRecordingStopped) {
                    this.onRecordingStopped(data);
                }
                break;
                
            case 'screen_share_started':
                if (this.onScreenShareStarted) {
                    this.onScreenShareStarted(data);
                }
                break;
                
            case 'screen_share_stopped':
                if (this.onScreenShareStopped) {
                    this.onScreenShareStopped(data);
                }
                break;
                
            case 'participant_media_changed':
                // Handle remote participant media state changes
                this._log('Participant media changed', data);
                break;
        }
    }
    
    _broadcastMediaState() {
        const mediaState = this.getMediaState();
        this.socket.emit('webrtc_signal', {
            type: 'media_state_change',
            is_audio_muted: mediaState.isAudioMuted,
            is_video_muted: mediaState.isVideoMuted
        });
    }
    
    _handleError(message, error = null) {
        const errorMessage = error ? `${message}: ${error}` : message;
        this._log(errorMessage, 'error');
        
        if (this.onError) {
            this.onError(errorMessage, error);
        }
    }
    
    _log(message, level = 'info') {
        if (this.config.debug) {
            console[level](`[WebRTC Client] ${message}`);
        }
    }
}

// Export for use in applications
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebRTCClient;
} else {
    window.WebRTCClient = WebRTCClient;
}