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

// ----------- VIDEO DECRYPTING ---------------
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

async function decryptKeys() {
    const sessionKeyBytes = hexToBytes(sessionKey);
    const wrappedMasterKeyBytes = hexToBytes(videoKey);
    const wrapNonceBytes = hexToBytes(videoNonce);

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
        {name: "AES-GCM", iv: wrapNonceBytes},
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

    return masterKey;
}


async function fetchAndDecryptShard(shardMeta, videoMasterKey) {
    console.log(shardMeta)

    // 1. Fetch encrypted shard
    const response = await fetch(shardMeta.url);
    const encryptedBytes = new Uint8Array(await response.arrayBuffer());

    // 2. Convert nonce
    const nonceBytes = hexToBytes(shardMeta.nonce);

    // 3. Decrypt shard with master key
    const decryptedBytesBuffer = await crypto.subtle.decrypt(
        {name: "AES-GCM", iv: nonceBytes},
        videoMasterKey,
        encryptedBytes
    );

    const decryptedBytes = new Uint8Array(decryptedBytesBuffer);

    // 4. Reverse scramble / XOR
    const unscrambled = decryptedBytes.map(byte => {
        // Step 1: Rotate bits left
        const rotated = ((byte >> 3) | (byte << 5)) & 0xFF;

        // Step 2: XOR with the mask from shardMeta
        const result = rotated ^ shardMeta.mask;

        // Step 3: Return the result
        return result;
    });

    // saveUnscrambledShard(unscrambled, shardMeta.name + '.mp4')
    return unscrambled;
}

function saveUnscrambledShard(arrayBuffer, fileName = "shard.mp4") {
    // Convert ArrayBuffer to Blob
    const blob = new Blob([arrayBuffer], {type: "video/mp4"});

    // Create a temporary link
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = fileName;

    // Trigger download
    document.body.appendChild(link); // required for Firefox
    link.click();

    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
}

function maskAndOrder() {
    shards = []
    videoMetadata.shards.forEach((shard) => {
        name = shard['name'];
        split_name = name.split('_')

        index = split_name[1].slice(4)
        mask = split_name[2].slice(4)

        shard['mask'] = mask // mask is integer number
        shards[index] = shard
    });

    return shards;
}


// -------------------- VIDEO PLAYER -----------------------
const player = videojs('my-video');

// Resize player to fit viewable screen
player.ready(function () {
    player.on('loadedmetadata', function () {
        resizeVideo();
    });
});

// Re-run on window resize
window.addEventListener('resize', resizeVideo);

// Start feeding shard
const mediaSource = new MediaSource();
player.src({src: URL.createObjectURL(mediaSource), type: 'video/mp4'});

mediaSource.addEventListener("sourceopen", async () => {
    // Replace with the correct codec for your shard
    const sourceBuffer = mediaSource.addSourceBuffer(videoMetadata.codec);

    // Suppose you already have the unscrambled shard as ArrayBuffer
    const shards = maskAndOrder()
    shard = shards[0];
    const videoMasterKey = await decryptKeys();
    const shardBytes = await fetchAndDecryptShard(shard, videoMasterKey);

    // Only append if MediaSource is open
    if (mediaSource.readyState === "open") {
        sourceBuffer.appendBuffer(shardBytes);
    }

    // Wait for the append to finish before ending stream
    sourceBuffer.addEventListener("updateend", () => {
        if (mediaSource.readyState === "open") {
            mediaSource.endOfStream();
        }
    }, {once: true});
});
// mediaSource.addEventListener("sourceopen", async () => {
//     const sourceBuffer = mediaSource.addSourceBuffer(videoMetadata.codec);
//     const videoMasterKey = await decryptKeys();
//     const queue = [];
//     let ended = false;
//
//     function appendNext() {
//         if (!sourceBuffer.updating && queue.length > 0 && mediaSource.readyState === "open") {
//             sourceBuffer.appendBuffer(queue.shift());
//         } else if (!sourceBuffer.updating && queue.length === 0 && ended) {
//             mediaSource.endOfStream();
//         }
//     }
//
//     sourceBuffer.addEventListener("updateend", appendNext);
//
//     // Start fetching shards without awaiting
//     maskAndOrder().forEach(async (shardMeta) => {
//         const shardBytes = await fetchAndDecryptShard(shardMeta, videoMasterKey);
//         queue.push(shardBytes);
//         appendNext();
//     });
//
//     // Signal that all shards are queued eventually
//     ended = true;
// });
