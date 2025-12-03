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

function hexToBytes(hex) {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < hex.length; i += 2) {
        bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
    }
    return bytes;
}


// ----------- VIDEO DECRYPTING ---------------

const sessionKeyBytes = hexToBytes(sessionKey)
const videoKeyBytes = hexToBytes(videoKey)
const videoNonceBytes = hexToBytes(videoNonce)

async function decryptKeys() {
    // Import session key as AES-GCM key
    const cryptoKey = await crypto.subtle.importKey(
        "raw",
        sessionKeyBytes,
        "AES-GCM",
        false,
        ["decrypt"]
    );

    // Decrypt the wrapped master key
    const masterKeyBytes = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: wrapNonceBytes, additionalData: null },
        cryptoKey,
        wrappedMasterKeyBytes
    );

    // Import master key to decrypt shards
    const masterKey = await crypto.subtle.importKey(
        "raw",
        masterKeyBytes,
        "AES-GCM",
        false,
        ["decrypt"]
    );
}


async function fetchAndDecryptShard(shardMeta) {
    // 1. Fetch encrypted shard
    const response = await fetch(shardMeta.shard_url);
    const encryptedBytes = new Uint8Array(await response.arrayBuffer());

    // 2. Convert nonce
    const nonceBytes = hexToBytes(shardMeta.nonce);

    // 3. Decrypt shard with master key
    const decryptedBytesBuffer = await crypto.subtle.decrypt(
        { name: "AES-GCM", iv: nonceBytes, additionalData: null },
        masterKey,
        encryptedBytes
    );

    const decryptedBytes = new Uint8Array(decryptedBytesBuffer);

    // 4. Reverse scramble / XOR
    const unscrambled = decryptedBytes.map(byte => ((byte >> 3) | (byte << 5)) & 0xFF ^ shardMeta.mask);

    return unscrambled;
}

// -------------------- VIDEO PLAYER -----------------------
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
mediaSource.addEventListener("sourceopen", () => {
    window.buffer = mediaSource.addSourceBuffer(videoCodec); // defined in single_media.htm
});


