function fileUploaderComponent(uploadApi, userSuggestionApi, myContentUrl) {
    return {
        files: [],           // all files in the UI (including uploaded)
        uploadedFiles: [],   // track files already uploaded
        isUploading: false,
        userSuggestionComponent: null,

        init() {
            // call after Alpine has initialized this component
            this.userSuggestionComponent = userSuggestionComponent(
                userSuggestionApi,
                (fileIndex, descriptionValue) => {
                    this.files[fileIndex]['description'] = descriptionValue;
                },
            )
        },

        handleFiles(event) {
            const selectedFiles = Array.from(event.target.files);

            selectedFiles.forEach(file => {
                // skip files that are already uploaded
                if (this.uploadedFiles.some(f => f.name === file.name && f.size === file.size)) return;
                const fileType = file.type.startsWith("image/") ? "image" : "video";
                const unlockPriceInFiat = 0;

                const fileData = {
                    file: file,
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    preview: URL.createObjectURL(file),
                    progress: 0,
                    description: null,
                    status: 'pending',          // pending | uploading | finalizing | completed | failed
                    statusMessage: '',
                    unlockPriceInFiat: unlockPriceInFiat
                };
                this.files.push(fileData);
            });

            event.target.value = '';
        },

        uploadFile(fileData, postType) {
            // skip if already uploaded
            if (fileData.status === 'completed') return;

            fileData.status = 'uploading';
            fileData.statusMessage = 'Uploading…';

            const formData = new FormData();
            formData.append('postType', postType);
            formData.append('file', fileData.file);
            formData.append('unlockPriceInFiat', fileData.unlockPriceInFiat);
            if (fileData.description !== null) {
                formData.append('description', fileData.description);
            }

            const xhr = new XMLHttpRequest();
            console.log(getCsrfToken())
            xhr.open("POST", uploadApi);
            xhr.setRequestHeader("X-CSRFToken", getCsrfToken());

            xhr.upload.addEventListener("progress", (e) => {
                if (e.lengthComputable) {
                    fileData.progress = Math.round((e.loaded / e.total) * 100);
                    if (fileData.progress === 100) {
                        fileData.statusMessage = "Finalizing upload…";
                        fileData.status = 'finalizing';
                    }
                }
            });

            xhr.onload = () => {
                if (xhr.status === 200) {
                    fileData.statusMessage = "✅ Upload complete! Visit <a href ='"+myContentUrl+"' class='underline font-bold'>My Content</a> to make updates and send consent requests to other creators. ";
                    fileData.status = 'completed';

                    // add to uploadedFiles array to prevent re-upload
                    if (!this.uploadedFiles.includes(fileData)) {
                        this.uploadedFiles.push(fileData);
                    }

                    allUploaded = true
                    this.files.forEach(file => {
                        if (file.status !== 'completed') {
                            allUploaded = false;
                        }
                    });
                    if (allUploaded) {
                        this.isUploading = false;
                    }
                } else {
                    fileData.statusMessage = "Upload failed ❌";
                    fileData.status = 'failed';
                }
            };

            xhr.onerror = () => {
                fileData.statusMessage = "Upload error ❌";
                fileData.status = 'failed';
            };

            xhr.send(formData);
        },

        uploadAllFiles(postType) {
            if (this.files.length === 0) {
                alert('Choose some files');
                return;
            }
            this.isUploading = true;
            this.files.forEach(file => {
                if (file.status !== 'completed') {
                    this.uploadFile(file, postType);
                }
            });
        }
    }
}
