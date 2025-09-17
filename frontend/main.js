document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('queryForm');
    const submitBtn = document.getElementById('submitBtn');
    const textResponse = document.getElementById('textResponse');
    const audioResponse = document.getElementById('audioResponse');
    const spinner = document.getElementById('spinner');
    const responseSection = document.getElementById('responseSection');
    const successIndicator = document.querySelector('.success-indicator');
    const newQueryBtn = document.getElementById('newQueryBtn');
    const audioHelp = document.getElementById('audioHelp');
    
    // Audio recording variables
    let mediaRecorder;
    let recordedChunks = [];
    let recording = false;
    let recordingTimer;
    let recordingTime = 0;
    
    const recordBtn = document.getElementById('recordBtn');
    const recordTime = document.getElementById('recordTime');
    const recordingStatus = document.getElementById('recordingStatus');
    const recordedAudio = document.getElementById('recordedAudio');
    
    // Character counter for textarea
    const textInput = document.getElementById('textInput');
    const textHelp = document.getElementById('textHelp');
    
    textInput.addEventListener('input', function() {
        const remaining = 5000 - this.value.length;
        textHelp.textContent = `${remaining} characters remaining • ${remaining} अक्षर शेष`;
        textHelp.style.color = remaining < 100 ? 'var(--warning)' : 'var(--text-muted)';
    });

    // Audio Recording Functionality
    recordBtn.addEventListener('click', async function() {
        if (!recording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                recordedChunks = [];
                
                mediaRecorder.ondataavailable = function(event) {
                    if (event.data.size > 0) {
                        recordedChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = function() {
                    const blob = new Blob(recordedChunks, { type: 'audio/wav' });
                    const audioUrl = URL.createObjectURL(blob);
                    recordedAudio.src = audioUrl;
                    recordedAudio.style.display = 'block';
                    
                    // Create a file for form submission
                    const file = new File([blob], 'recording.wav', { type: 'audio/wav' });
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    document.getElementById('audioInput').files = dt.files;
                };
                
                // Start recording
                mediaRecorder.start();
                recording = true;
                recordBtn.classList.add('recording');
                recordBtn.textContent = '⏹️';
                recordBtn.title = 'Stop Recording';
                recordingStatus.textContent = 'Recording... Click to stop • रिकॉर्डिंग... रोकने के लिए क्लिक करें';
                recordingTime = 0;
                
                recordingTimer = setInterval(() => {
                    recordingTime++;
                    const minutes = Math.floor(recordingTime / 60);
                    const seconds = recordingTime % 60;
                    recordTime.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                }, 1000);
                
            } catch (error) {
                console.error('Error accessing microphone:', error);
                recordingStatus.textContent = 'Error: Could not access microphone. Please check permissions. • त्रुटि: माइक्रोफोन तक पहुंच नहीं। कृपया अनुमतियां जांचें।';
                recordingStatus.style.color = 'var(--error)';
            }
        } else {
            // Stop recording
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            recording = false;
            recordBtn.classList.remove('recording');
            recordBtn.textContent = '🎤';
            recordBtn.title = 'Start Recording';
            recordingStatus.textContent = 'Recording complete! You can play it back or record again. • रिकॉर्डिंग पूर्ण! आप इसे वापस चला सकते हैं या फिर से रिकॉर्ड कर सकते हैं।';
            recordingStatus.style.color = 'var(--success)';
            clearInterval(recordingTimer);
        }
    });

    function markdownToHtml(text) {
        // Enhanced markdown parsing
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert lines starting with * or - to list items
        if (/^\s*([*-])\s+/m.test(text)) {
            const lines = text.split(/\r?\n/);
            let inList = false;
            let html = '';
            for (const line of lines) {
                if (/^\s*([*-])\s+/.test(line)) {
                    if (!inList) { html += '<ul>'; inList = true; }
                    html += '<li>' + line.replace(/^\s*([*-])\s+/, '') + '</li>';
                } else {
                    if (inList) { html += '</ul>'; inList = false; }
                    if (line.trim()) {
                        html += '<p>' + line + '</p>';
                    }
                }
            }
            if (inList) { html += '</ul>'; }
            return html;
        }
        
        // Convert line breaks to paragraphs
        const paragraphs = text.split(/\n\s*\n/);
        return paragraphs.map(p => p.trim() ? `<p>${p.replace(/\n/g, '<br>')}</p>` : '').join('');
    }

    function showLoadingState() {
        submitBtn.disabled = true;
        spinner.style.display = 'block';
        responseSection.style.display = 'none';
        textResponse.innerHTML = '';
        audioResponse.style.display = 'none';
        audioResponse.src = '';
        successIndicator.style.display = 'none';
        newQueryBtn.style.display = 'none';
        audioHelp.style.display = 'none';
    }

    function showResponse(data) {
        spinner.style.display = 'none';
        responseSection.style.display = 'block';
        
        if (data.text) {
            textResponse.innerHTML = markdownToHtml(data.text);
            successIndicator.style.display = 'block';
        }
        
        if (data.audio) {
            audioResponse.src = data.audio;
            audioResponse.style.display = 'block';
            audioHelp.style.display = 'block';
        }
        
        newQueryBtn.style.display = 'block';
        
        // Smooth scroll to response
        setTimeout(() => {
            responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    function showError(message) {
        spinner.style.display = 'none';
        responseSection.style.display = 'block';
        textResponse.innerHTML = `<div class="error-message">${message}</div>`;
        newQueryBtn.style.display = 'block';
        
        setTimeout(() => {
            responseSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate form
        const text = textInput.value.trim();
        const image = document.getElementById('imageInput').files[0];
        const audio = document.getElementById('audioInput').files[0];
        
        if (!text && !image && !audio) {
            showError('Please provide at least one input (text, image, or audio).');
            return;
        }
        
        showLoadingState();
        
        const formData = new FormData(form);
        const apiUrl = window.location.origin + '/api/query';
        
        try {
            const res = await fetch(apiUrl, {
                method: 'POST',
                body: formData
            });
            
            const data = await res.json();
            
            if (!res.ok) {
                throw new Error(data.detail || `API error: ${res.status}`);
            }
            
            if (data.status === 'success' || data.text) {
                showResponse(data);
            } else {
                throw new Error(data.text || 'Unknown error occurred');
            }
            
        } catch (err) {
            console.error('Request failed:', err);
            showError(err.message || 'Network error. Please check your connection and try again.');
        } finally {
            submitBtn.disabled = false;
        }
    });
    
    // File size validation
    function validateFileSize(file, maxSize = 10 * 1024 * 1024) { // 10MB
        if (file && file.size > maxSize) {
            return false;
        }
        return true;
    }
    
    // Add file size validation listeners
    document.getElementById('imageInput').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file && !validateFileSize(file)) {
            alert('Image file is too large. Maximum size is 10MB.');
            e.target.value = '';
        }
    });
    
    document.getElementById('audioInput').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file && !validateFileSize(file)) {
            alert('Audio file is too large. Maximum size is 10MB. • ऑडियो फ़ाइल बहुत बड़ी है। अधिकतम आकार 10MB है।');
            e.target.value = '';
        } else if (file) {
            recordingStatus.textContent = `Audio file selected: ${file.name} • ऑडियो फ़ाइल चुनी गई: ${file.name}`;
            recordingStatus.style.color = 'var(--success)';
            recordedAudio.style.display = 'none';
        }
    });
});

// Global function for "Ask Another Question" button
function startNewQuery() {
    document.getElementById('queryForm').reset();
    document.getElementById('responseSection').style.display = 'none';
    document.getElementById('recordedAudio').style.display = 'none';
    document.getElementById('textHelp').textContent = 'Maximum 5000 characters • अधिकतम 5000 अक्षर';
    document.getElementById('textHelp').style.color = 'var(--text-muted)';
    document.getElementById('recordingStatus').textContent = 'Click the microphone to start recording • रिकॉर्डिंग शुरू करने के लिए माइक्रोफोन पर क्लिक करें';
    document.getElementById('recordingStatus').style.color = 'var(--text-muted)';
    document.getElementById('recordTime').textContent = '00:00';
    
    // Scroll back to form
    document.querySelector('.form-card').scrollIntoView({ behavior: 'smooth', block: 'start' });
}