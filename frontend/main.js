document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('queryForm');
    const submitBtn = document.getElementById('submitBtn');
    const textResponse = document.getElementById('textResponse');
    const audioResponse = document.getElementById('audioResponse');
    const spinner = document.getElementById('spinner');

    function markdownToHtml(text) {
        // Convert *text* to <b>text</b>
        text = text.replace(/\*(.*?)\*/g, '<b>$1</b>');
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
                    html += line + '<br>';
                }
            }
            if (inList) { html += '</ul>'; }
            return html;
        }
        return text.replace(/\r?\n/g, '<br>');
    }

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        submitBtn.disabled = true;
        spinner.style.display = 'block';
        textResponse.innerHTML = '';
        audioResponse.style.display = 'none';
        audioResponse.src = '';

        const formData = new FormData(form);
        const apiUrl = window.location.origin + '/api/query';
        try {
            const res = await fetch(apiUrl, {
                method: 'POST',
                body: formData
            });
            if (!res.ok) {
                throw new Error('API error: ' + res.status);
            }
            const data = await res.json();
            textResponse.innerHTML = markdownToHtml(data.text || 'No response.');
            if (data.audio) {
                audioResponse.src = data.audio;
                audioResponse.style.display = 'block';
            }
        } catch (err) {
            textResponse.innerHTML = 'Error: ' + err.message;
        } finally {
            submitBtn.disabled = false;
            spinner.style.display = 'none';
        }
    });
});
