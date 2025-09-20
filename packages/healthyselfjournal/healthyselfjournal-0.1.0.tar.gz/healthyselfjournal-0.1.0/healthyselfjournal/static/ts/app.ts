/*
 * Minimal browser recorder for the Healthy Self Journal web interface.
 * Handles MediaRecorder capture, simple level metering, and uploads to the FastHTML server.
 */

type RecorderState = 'idle' | 'recording' | 'uploading';

type UploadResponse = UploadSuccessResponse | UploadErrorResponse;

interface RecorderConfig {
  uploadUrl: string;
  sessionId: string;
  shortDurationMs: number;
  shortVoicedMs: number;
}

interface DOMElements {
  recordButton: HTMLButtonElement;
  statusText: HTMLElement;
  meterBar: HTMLElement;
  currentQuestion: HTMLElement;
  historyList: HTMLElement;
}

interface UploadSuccessResponse {
  status: 'ok';
  session_id: string;
  segment_label: string;
  duration_seconds: number;
  transcript: string;
  next_question: string;
  llm_model?: string | null;
  summary_scheduled?: boolean;
}

interface UploadErrorResponse {
  status: 'error';
  error: string;
  detail?: string;
}

class RecorderController {
  private state: RecorderState = 'idle';
  private mediaStream?: MediaStream;
  private mediaRecorder?: MediaRecorder;
  private audioContext?: AudioContext;
  private analyser?: AnalyserNode;
  private analyserBuffer?: Uint8Array;
  private sourceNode?: MediaStreamAudioSourceNode;
  private meterRafId?: number;
  private chunks: BlobPart[] = [];
  private startTimestamp = 0;
  private voicedMs = 0;
  private lastMeterSample = 0;
  private cancelFlag = false;
  private readonly voicedThreshold = 0.07; // heuristic amplitude threshold 0-1

  constructor(private readonly elements: DOMElements, private readonly config: RecorderConfig) {
    this.elements.recordButton.addEventListener('click', () => {
      void this.toggleRecording();
    });

    window.addEventListener('keydown', (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        this.cancelRecording();
      }
    });

    if (!navigator.mediaDevices?.getUserMedia) {
      this.fail('Microphone access is not supported in this browser.');
    }

    if (typeof MediaRecorder === 'undefined') {
      this.fail('MediaRecorder is unavailable. Please use a modern Chromium-based browser.');
    }
  }

  private fail(message: string): void {
    this.setStatus(message);
    this.elements.recordButton.disabled = true;
  }

  private async toggleRecording(): Promise<void> {
    if (this.state === 'uploading') {
      return;
    }
    if (this.state === 'idle') {
      await this.startRecording();
      return;
    }
    if (this.state === 'recording') {
      this.stopRecording();
    }
  }

  private async startRecording(): Promise<void> {
    try {
      this.elements.recordButton.disabled = true;
      if (!this.mediaStream) {
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
      }
      if (!this.audioContext) {
        this.audioContext = new AudioContext();
      }
      await this.audioContext.resume();

      this.sourceNode = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      this.sourceNode.connect(this.analyser);
      this.analyserBuffer = new Uint8Array(this.analyser.fftSize);

      const mimeType = this.chooseMimeType();
      this.mediaRecorder = new MediaRecorder(this.mediaStream, { mimeType });
      this.mediaRecorder.addEventListener('dataavailable', this.handleDataAvailable);
      this.mediaRecorder.addEventListener('stop', this.handleStop);

      this.chunks = [];
      this.voicedMs = 0;
      this.lastMeterSample = performance.now();
      this.startTimestamp = performance.now();
      this.mediaRecorder.start();

      this.state = 'recording';
      this.elements.recordButton.disabled = false;
      this.elements.recordButton.textContent = 'Stop recording';
      this.elements.recordButton.dataset.state = 'recording';
      this.setStatus('Recording… Press stop when you are done.');
      this.startMeterLoop();
    } catch (error) {
      console.error('Failed to start recording', error);
      this.setStatus('Microphone permission denied or recorder unavailable.');
      this.resetButton();
    }
  }

  private stopRecording(): void {
    if (this.state !== 'recording' || !this.mediaRecorder) {
      return;
    }
    this.state = 'uploading';
    this.cancelFlag = false;
    this.elements.recordButton.disabled = true;
    this.elements.recordButton.textContent = 'Processing…';
    this.elements.recordButton.dataset.state = 'uploading';
    this.setStatus('Processing audio…');
    this.stopMeterLoop();
    this.mediaRecorder.stop();
  }

  private cancelRecording(): void {
    if (this.state !== 'recording' || !this.mediaRecorder) {
      return;
    }
    this.cancelFlag = true;
    this.state = 'idle';
    this.stopMeterLoop();
    this.mediaRecorder.stop();
  }

  private handleDataAvailable = (event: BlobEvent): void => {
    if (event.data && event.data.size > 0) {
      this.chunks.push(event.data);
    }
  };

  private handleStop = async (): Promise<void> => {
    const blob = new Blob(this.chunks, {
      type: this.mediaRecorder?.mimeType || 'audio/webm;codecs=opus',
    });
    this.chunks = [];

    if (this.mediaRecorder) {
      this.mediaRecorder.removeEventListener('dataavailable', this.handleDataAvailable);
      this.mediaRecorder.removeEventListener('stop', this.handleStop);
      this.mediaRecorder = undefined;
    }

    if (this.sourceNode) {
      this.sourceNode.disconnect();
      this.sourceNode = undefined;
    }

    const durationMs = Math.max(performance.now() - this.startTimestamp, 0);
    const voicedMs = this.voicedMs;
    this.voicedMs = 0;
    this.lastMeterSample = 0;

    if (this.cancelFlag) {
      this.cancelFlag = false;
      this.resetButton();
      this.setStatus('Recording cancelled.');
      this.state = 'idle';
      return;
    }

    if (durationMs < this.config.shortDurationMs || voicedMs < this.config.shortVoicedMs) {
      this.resetButton();
      this.setStatus('Discarded a very short or quiet clip. Try again when ready.');
      this.state = 'idle';
      return;
    }

    this.setStatus('Uploading clip…');
    this.elements.recordButton.textContent = 'Uploading…';
    this.elements.recordButton.disabled = true;

    try {
      const response = await this.uploadClip(blob, durationMs, voicedMs);
      if (response.status !== 'ok') {
        throw new Error(response.error || 'Unknown upload error');
      }
      this.setStatus('Thinking about the next question…');
      this.handleUploadSuccess(response, durationMs);
      this.setStatus('Ready for the next reflection.');
    } catch (error) {
      console.error('Upload failed', error);
      this.setStatus('Upload failed. Please check your connection and try again.');
    } finally {
      this.resetButton();
      this.state = 'idle';
    }
  };

  private startMeterLoop(): void {
    if (!this.analyser || !this.analyserBuffer) {
      return;
    }

    const update = (): void => {
      if (!this.analyser || !this.analyserBuffer) {
        return;
      }
      this.analyser.getByteTimeDomainData(this.analyserBuffer);
      let sumSquares = 0;
      for (let i = 0; i < this.analyserBuffer.length; i += 1) {
        const value = this.analyserBuffer[i] - 128;
        sumSquares += value * value;
      }
      const rms = Math.sqrt(sumSquares / this.analyserBuffer.length) / 128;
      const level = Math.min(1, rms * 2);
      this.setMeterLevel(level);

      const now = performance.now();
      const delta = Math.max(now - this.lastMeterSample, 0);
      if (rms > this.voicedThreshold) {
        this.voicedMs += delta;
      }
      this.lastMeterSample = now;

      if (this.state === 'recording') {
        this.meterRafId = requestAnimationFrame(update);
      } else {
        this.setMeterLevel(0);
      }
    };

    this.lastMeterSample = performance.now();
    this.meterRafId = requestAnimationFrame(update);
  }

  private stopMeterLoop(): void {
    if (this.meterRafId !== undefined) {
      cancelAnimationFrame(this.meterRafId);
      this.meterRafId = undefined;
    }
    this.setMeterLevel(0);
  }

  private async uploadClip(blob: Blob, durationMs: number, voicedMs: number): Promise<UploadResponse> {
    const form = new FormData();
    const filename = `browser-${Date.now()}.webm`;
    form.append('audio', blob, filename);
    form.append('mime', blob.type || 'audio/webm');
    form.append('duration_ms', durationMs.toString());
    form.append('voiced_ms', voicedMs.toString());
    form.append('question', this.elements.currentQuestion.textContent ?? '');

    const response = await fetch(this.config.uploadUrl, {
      method: 'POST',
      body: form,
    });

    const payload = (await response.json()) as UploadResponse;
    if (!response.ok) {
      throw new Error(
        payload.status === 'error'
          ? payload.error
          : `Upload failed with status ${response.status}`,
      );
    }
    return payload;
  }

  private handleUploadSuccess(payload: UploadSuccessResponse, durationMs: number): void {
    const answeredQuestion = this.elements.currentQuestion.textContent ?? '';
    this.elements.currentQuestion.textContent = payload.next_question;

    const historyItem = document.createElement('article');
    historyItem.className = 'hsj-exchange';

    const qHeading = document.createElement('h3');
    qHeading.textContent = 'AI';
    const qBody = document.createElement('p');
    qBody.textContent = answeredQuestion;

    const aHeading = document.createElement('h3');
    aHeading.textContent = 'You';
    const aBody = document.createElement('p');
    aBody.textContent = payload.transcript;

    const meta = document.createElement('p');
    meta.className = 'hsj-exchange-meta';
    meta.textContent = `Segment ${payload.segment_label} · ${(durationMs / 1000).toFixed(1)}s`;

    historyItem.append(qHeading, qBody, aHeading, aBody, meta);
    this.elements.historyList.prepend(historyItem);
  }

  private chooseMimeType(): string {
    const preferred = 'audio/webm;codecs=opus';
    if (MediaRecorder.isTypeSupported?.(preferred)) {
      return preferred;
    }
    return 'audio/webm';
  }

  private setMeterLevel(level: number): void {
    this.elements.meterBar.style.setProperty('--meter-level', level.toString());
  }

  private setStatus(message: string): void {
    this.elements.statusText.textContent = message;
  }

  private resetButton(): void {
    this.elements.recordButton.disabled = false;
    this.elements.recordButton.textContent = 'Start recording';
    this.elements.recordButton.dataset.state = 'idle';
  }
}

function bootstrap(): void {
  const body = document.body;
  const uploadUrl = body.dataset.uploadUrl;
  const sessionId = body.dataset.sessionId;
  if (!uploadUrl || !sessionId) {
    console.error('Missing session metadata on <body>.');
    return;
  }

  const shortDurationSeconds = Number(body.dataset.shortDuration ?? '1.2');
  const shortVoicedSeconds = Number(body.dataset.shortVoiced ?? '0.6');

  const elements: DOMElements = {
    recordButton: document.getElementById('record-button') as HTMLButtonElement,
    statusText: document.getElementById('status-text') as HTMLElement,
    meterBar: document.querySelector('#level-meter .bar') as HTMLElement,
    currentQuestion: document.getElementById('current-question') as HTMLElement,
    historyList: document.getElementById('history-list') as HTMLElement,
  };

  if (!elements.recordButton || !elements.statusText || !elements.meterBar) {
    console.error('Missing critical DOM elements.');
    return;
  }

  const config: RecorderConfig = {
    uploadUrl,
    sessionId,
    shortDurationMs: shortDurationSeconds * 1000,
    shortVoicedMs: shortVoicedSeconds * 1000,
  };

  new RecorderController(elements, config);
}

document.addEventListener('DOMContentLoaded', bootstrap);
