function singleMediaComponent() {
    return {
        liked: false,
        likes: 1200,
        comments: 345,

        like() {
            this.liked = true;
            this.likes += 1;

            // Animate the icon
            const icon = event.currentTarget.querySelector('i');
            icon.classList.add('scale-125');
            setTimeout(() => icon.classList.remove('scale-125'), 150);
        },

        comment() {
            this.comments += 1;

            // Animate the icon
            const icon = event.currentTarget.querySelector('i');
            icon.classList.add('scale-125');
            setTimeout(() => icon.classList.remove('scale-125'), 150);
        },

        report() {
            alert("Reported!");
        }
    }
}

function resizeVideo() {
    const video = document.getElementById('my-video');
    const windowWidth = window.innerWidth - 40;
    const windowHeight = window.innerHeight;

    // Get video original aspect ratio
    const videoAspect = video.videoWidth / video.videoHeight;
    const windowAspect = windowWidth / windowHeight;

    if (videoAspect > windowAspect) {
        // Video is wider than viewport → fit width
        video.style.width = windowWidth + 'px';
        video.style.height = (windowWidth / videoAspect) + 'px';
    } else {
        // Video is taller than viewport → fit height
        video.style.height = windowHeight + 'px';
        video.style.width = (windowHeight * videoAspect) + 'px';
    }
}

const player = videojs('my-video');

// Resize player to fit viewable screen
player.ready(function() {
    player.on('loadedmetadata', function() {
        resizeVideo();
    });
});

// Re-run on window resize
window.addEventListener('resize', resizeVideo);

// Start feeding shard
const mediaSource = new MediaSource();
player.src({ src: URL.createObjectURL(mediaSource), type: 'video/mp4' });