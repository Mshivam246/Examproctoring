(function () {
    const config = window.EXAM_PROCTOR_CONFIG;
    if (!config) {
        return;
    }

    const videoEl = document.getElementById("webcam");
    const statusEl = document.getElementById("proctor-status");
    const fullscreenButton = document.getElementById("fullscreen-btn");

    let detectorModel = null;
    let mediaStream = null;
    let audioContext = null;

    async function postEvent(eventType, severity, metadata) {
        try {
            await fetch(config.eventEndpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": config.csrfToken,
                },
                body: JSON.stringify({
                    exam_id: config.examId,
                    event_type: eventType,
                    severity: severity || "medium",
                    metadata: metadata || {},
                }),
            });
        } catch (error) {
            console.error("Failed to post proctor event", error);
        }
    }

    async function initializeCamera() {
        try {
            mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 },
                audio: true,
            });
            videoEl.srcObject = mediaStream;
            statusEl.textContent = "Camera and microphone are active.";
        } catch (error) {
            statusEl.textContent = "Camera access failed. Contact exam admin.";
            await postEvent("camera_error", "high", { message: error.message });
        }
    }

    async function initializeDetector() {
        try {
            detectorModel = await cocoSsd.load();
            statusEl.textContent = "AI proctoring initialized.";
        } catch (error) {
            statusEl.textContent = "AI detector failed to load.";
            console.error(error);
        }
    }

    async function detectPersons() {
        if (!detectorModel || !videoEl || videoEl.readyState < 2) {
            return;
        }

        const predictions = await detectorModel.detect(videoEl);
        const persons = predictions.filter((item) => item.class === "person");

        if (persons.length === 0) {
            await postEvent("no_person", "high", { count: 0 });
        }

        if (persons.length > 1) {
            await postEvent("multiple_person", "high", { count: persons.length });
        }
    }

    async function initializeNoiseMonitor() {
        if (!mediaStream) {
            return;
        }

        try {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioContext.createAnalyser();
            const microphone = audioContext.createMediaStreamSource(mediaStream);
            const dataArray = new Uint8Array(analyser.fftSize);

            microphone.connect(analyser);

            setInterval(async () => {
                analyser.getByteTimeDomainData(dataArray);
                let sum = 0;
                for (let i = 0; i < dataArray.length; i += 1) {
                    const value = (dataArray[i] - 128) / 128;
                    sum += value * value;
                }
                const rms = Math.sqrt(sum / dataArray.length);
                if (rms > 0.25) {
                    await postEvent("high_noise", "medium", { rms: Number(rms.toFixed(3)) });
                }
            }, 6000);
        } catch (error) {
            console.error("Noise monitor error", error);
        }
    }

    function initializeBehaviorChecks() {
        document.addEventListener("visibilitychange", async () => {
            if (document.hidden) {
                await postEvent("tab_switch", "high", {});
            }
        });

        window.addEventListener("blur", async () => {
            await postEvent("window_blur", "medium", {});
        });

        document.addEventListener("fullscreenchange", async () => {
            if (!document.fullscreenElement) {
                await postEvent("fullscreen_exit", "high", {});
            }
        });
    }

    async function requestFullscreen() {
        const rootElement = document.documentElement;
        if (rootElement.requestFullscreen) {
            await rootElement.requestFullscreen();
        }
    }

    async function start() {
        await initializeCamera();
        await initializeDetector();
        await initializeNoiseMonitor();
        initializeBehaviorChecks();

        setInterval(async () => {
            await detectPersons();
        }, 8000);
    }

    fullscreenButton.addEventListener("click", async () => {
        try {
            await requestFullscreen();
        } catch (error) {
            console.error(error);
        }
    });

    start();
})();
