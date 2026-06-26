import { parseStreamPath } from "@/lib/stream-utils";

export interface StreamPackageParams {
  streamPath: string;
  currentDomain: string;
  username: string;
  password: string;
  srtReadPassphrase: string;
}

export function getAtakRtmps({
  streamPath,
  currentDomain,
  username,
  password,
}: StreamPackageParams) {
  const { name: callsign } = parseStreamPath(streamPath);
  const uid = crypto.randomUUID();
  return `<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<feed>
<protocol>rtmps</protocol>
<alias>${callsign}</alias>
<uid>${uid}</uid>
<address>${currentDomain}</address>
<port>1936</port>
<roverPort>-1</roverPort>
<ignoreEmbeddedKLV>false</ignoreEmbeddedKLV>
<preferredMacAddress/>
<preferredInterfaceAddress/>
<path>${streamPath}?user=${username}&amp;pass=${password}</path>
<buffer>-1</buffer>
<timeout>1000</timeout>
<rtspReliable>0</rtspReliable>
</feed>
`;
}

export function getBrowserHls({
  streamPath,
  currentDomain,
  username,
  password,
}: StreamPackageParams) {
  return `\
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <title>Avaa HLS-stream</title>
    <meta http-equiv="refresh" content="0; url=https://${username}:${password}@${currentDomain}:9888${streamPath}">
  </head>
  <body>
    <p>Jos etäohjaus ei toimi automaattisesti, <a href="https://${username}:${password}@${currentDomain}:9888${streamPath}">klikkaa tästä avataksesi striimin</a>.</p>
  </body>
  </html>
`;
}

export function getVlcHls({
  streamPath,
  currentDomain,
  username,
  password,
}: StreamPackageParams) {
  return `\
  #EXTM3U
  #EXTINF:-1,/live/icu/test
  https://${username}:${password}@${currentDomain}:9888${streamPath}/index.m3u8
`;
}

export function getVlcSrt({
  streamPath,
  currentDomain,
  username,
  password,
  srtReadPassphrase,
}: StreamPackageParams) {
  const fixedPath = streamPath.slice(1);
  return `\
  #EXTM3U
  #EXTINF:-1,/live/icu/test
  srt://${currentDomain}:8890?streamid=read:${fixedPath}:${username}:${password}&passphrase=${srtReadPassphrase}`;
}
