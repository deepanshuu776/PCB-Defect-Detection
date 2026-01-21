const fileInput = document.getElementById('fileInput');
const analyzeBtn = document.getElementById('analyzeBtn');
const originalImg = document.getElementById('originalImg');
const processedImg = document.getElementById('processedImg');
const resultsArea = document.getElementById('resultsArea');
const defectCount = document.getElementById('defectCount');
const statusText = document.getElementById('statusText');
const defectList = document.getElementById('defectList');

// Select the text elements inside the dropzone
const dropZoneHeader = document.querySelector('#dropZone h3');
const dropZoneSubtext = document.querySelector('#dropZone p');
const dropZoneIcon = document.querySelector('#dropZone .icon');

let selectedFile = null;

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        selectedFile = e.target.files[0];
        
        // --- NEW CODE START: Update the UI with filename ---
        dropZoneHeader.textContent = "Selected: " + selectedFile.name;
        dropZoneSubtext.textContent = "Ready to analyze";
        dropZoneIcon.textContent = "📄"; // Change cloud icon to file icon
        dropZoneHeader.style.color = "#2563eb"; // Change color to blue to show active state
        // --- NEW CODE END ---

        originalImg.src = URL.createObjectURL(selectedFile);
        analyzeBtn.disabled = false;
        resultsArea.style.display = 'none';
    }
});

analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    analyzeBtn.textContent = "Analyzing...";
    analyzeBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            processedImg.src = `data:image/jpeg;base64,${data.image_base64}`;
            defectCount.textContent = data.defect_count;
            
            if (data.defect_count > 0) {
                statusText.textContent = "Defective ⚠️";
                statusText.style.color = "#ef4444";
            } else {
                statusText.textContent = "Clean ✅";
                statusText.style.color = "#10b981";
            }

            defectList.innerHTML = '';
            data.detections.forEach(det => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${det.class}</strong> <small>(Conf: ${(det.confidence * 100).toFixed(1)}%)</small>`;
                defectList.appendChild(li);
            });

            resultsArea.style.display = 'block';
        }
    } catch (error) {
        alert("Error connecting to server!");
        console.error(error);
    } finally {
        analyzeBtn.textContent = "Analyze Circuit";
        analyzeBtn.disabled = false;
    }
});