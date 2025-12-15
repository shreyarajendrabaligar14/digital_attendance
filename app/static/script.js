document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const cameraInput = document.getElementById('cameraInput');
    const triggerUpload = document.getElementById('trigger-upload');
    const triggerCamera = document.getElementById('trigger-camera');
    const processBtn = document.getElementById('processBtn');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');

    let selectedFile = null;

    // Verify elements exist
    if (!dropZone || !fileInput || !cameraInput) {
        console.error('Required elements not found');
        return;
    }

    console.log('Script loaded and events attached');

    // Button Handlers
    triggerUpload.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent bubbling to dropZone if we kept a listener there
        fileInput.click();
    });

    triggerCamera.addEventListener('click', (e) => {
        e.stopPropagation();
        cameraInput.click();
    });

    // Drag and drop handlers (Keep specific behaviors)
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drop-zone--over');
    });

    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drop-zone--over');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drop-zone--over');
        console.log('File dropped');

        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    cameraInput.addEventListener('change', (e) => {
        if (cameraInput.files.length) {
            handleFileSelect(cameraInput.files[0]);
        }
    });

    function handleFileSelect(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }
        selectedFile = file;
        dropZone.querySelector('.drop-zone__prompt').textContent = file.name;
        processBtn.disabled = false;
    }

    processBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Reset UI
        resultsDiv.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        processBtn.disabled = true;

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Upload failed');
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            alert('Error processing image: ' + error.message);
        } finally {
            loadingDiv.classList.add('hidden');
            processBtn.disabled = false;
        }
    });

    function displayResults(data) {
        document.getElementById('total-count').textContent = data.total_students;
        document.getElementById('present-count').textContent = data.present_count;
        document.getElementById('absent-count').textContent = data.absent_count;
        document.getElementById('unknown-count').textContent = data.unknown_faces_detected;

        const presentList = document.getElementById('present-list');
        presentList.innerHTML = data.present_students.map(s => `
            <li>
                <span><span class="roll">${s.roll_no}</span> ${s.name}</span>
                <span class="confidence">${s.match_confidence}%</span>
            </li>
        `).join('');

        const absentList = document.getElementById('absent-list');
        absentList.innerHTML = data.absent_students.map(s => `
            <li>
                <span><span class="roll">${s.roll_no}</span> ${s.name}</span>
            </li>
        `).join('');

        resultsDiv.classList.remove('hidden');
    }
});
