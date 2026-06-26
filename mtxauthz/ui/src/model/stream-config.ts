export interface Credentials {
  username: string;
  password: string;
  stream_ro_password: string;
}

export interface SrtPasswords {
  publish: string;
  read: string;
}

export type StreamConfig = {
  path: string;
  urls: {
    hls: string;
    webrtc: string;
    rtsps: string;
    rtmps: string;
    srt: string;
  };
};
