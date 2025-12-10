function mediaFeed(feedType, mediaApiUrl) {
    return {
        mediaList: [],
        page: 1,
        loadingMore: false,
        hasMore: true,

        async init() {
            await this.loadMore();

            // Observe footer for infinite scroll
            this.$nextTick(() => {
                const footer = document.querySelector('footer');   // <-- your request

                if (!footer) {
                    console.warn("Footer not found");
                    return;
                }

                const observer = new IntersectionObserver(
                    (entries) => {
                        if (entries[0].isIntersecting) this.loadMore();
                    },
                    { rootMargin: "200px" } // load when close to footer
                );

                observer.observe(footer);
            });
        },

        async loadMore() {
            if (this.loadingMore || !this.hasMore) return;

            this.loadingMore = true;
            try {
                const res = await fetch(`${mediaApiUrl}?page=${this.page}&type=${feedType}`);
                if (!res.ok) throw new Error("Failed to fetch media");

                const data = await res.json();
                const items = data.results || data;

                this.mediaList.push(...items);

                this.page = data.next_page ?? this.page + 1;
                this.hasMore = !!data.next_page;
            } catch (e) {
                console.error(e);
            } finally {
                this.loadingMore = false;
            }
        },

        formatCount(n) {
            if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
            if (n >= 1e3) return (n / 1e3).toFixed(1) + "K";
            return n;
        },

        async trackMediaView(mediaElement, media) {
            const isVideo = media.type === "video";
            const isImage = media.type === "image";

            if (isImage) {
                setTimeout(async () => {
                    try {
                        await fetch(recordViewsApi, {
                            method: "POST",
                            headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
                            credentials: "include",
                            body: JSON.stringify({ media_id: media.id }),
                        });
                    } catch (e) {
                        console.error("Failed to record image view", e);
                    }
                }, 2000);
            }

            if (isVideo) {
                const percentageToTrack = 50;
                const duration = mediaElement.duration;
                if (!duration || duration === Infinity) return;

                const targetTime = (percentageToTrack / 100) * duration;

                const onTimeUpdate = async () => {
                    if (mediaElement.currentTime >= targetTime) {
                        mediaElement.removeEventListener("timeupdate", onTimeUpdate);

                        try {
                            await fetch(recordViewsApi, {
                                method: "POST",
                                headers: { "Content-Type": "application/json", "X-CSRFToken": getCsrfToken() },
                                credentials: "include",
                                body: JSON.stringify({ media_id: media.id }),
                            });
                        } catch (e) {
                            console.error("Failed to record video view", e);
                        }
                    }
                };

                mediaElement.addEventListener("timeupdate", onTimeUpdate);
            }
        }
    }
}
