function myContentComponent(userSuggestionApi) {
    return {
        descriptions: [],
        userSuggestionComponent: null,
        init() {
            this.userSuggestionComponent = userSuggestionComponent(
                userSuggestionApi,
                (fileId, descriptionValue) => {
                    document.getElementById('description_field_' + fileId).value = descriptionValue;
                },
            )
        },
        copyLink(url) {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url)
                    .then(() => alert('Link copied!'))
                    .catch(err => console.error('Failed to copy: ', err));
            } else {
                // Fallback: use prompt to copy manually
                prompt("Copy this link:", url);
            }
        },
        async shareLink(url) {
            if (navigator.share) {
                try {
                    await navigator.share({
                        title: 'Consent Request',
                        text: 'Please review and give your consent for this content.',
                        url: url
                    });
                } catch (err) {
                    console.error('Error sharing:', err);
                }
            } else {
                alert('Your device does not support native sharing. You can copy the link instead.');
            }
        }
    }
}

 $(document).ready(function() {
        $('.media-block input[type="checkbox"]').change(function() {
            var parentDiv = $(this).closest('.media-block');
            if ($(this).is(':checked')) {
                parentDiv.addClass('bg-red-900');
            } else {
                parentDiv.removeClass('bg-red-900');
            }
        });
    });