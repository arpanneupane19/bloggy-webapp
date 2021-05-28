function likes(total) {
    if (total === 1) {
        return `${total} like`
    }

    if (total > 1 || total === 0) {
        return `${total} likes`
    }
}

function navigateToPage(path) {
    return window.location.assign(path)
}

$(document).ready(() => {
    $(".like-unlike").on("click", function () {
        var postId = $(this).attr("post_id")
        var action = $(this).attr("action");

        req = $.ajax({
            url: `/post/${postId}/${action}`,
            type: 'POST',
            data: { postId: postId, action: action }
        })



        req.done((data) => {
            document.querySelector(`.total-likes${postId}`).innerHTML = likes(data.total_likes)
            var likesTotal = document.querySelector(`.total-likes${postId}`)
            if (data.total_likes > 1 || data.total_likes === 1) {
                likesTotal.style.color = 'rgb(0,140,255)'
                likesTotal.style.cursor = 'pointer'
                $('.total-likes' + postId).on("click", function () {
                    navigateToPage(`/post/${postId}/view-likes`)
                })

            }
            else {
                likesTotal.style.color = '#000'
                likesTotal.style.cursor = 'auto'
                ableToViewLikes = false;
            }

            if (data.liked) {
                $(this).attr('action', 'unlike')
                document.querySelector(".toggle" + postId).innerHTML = "Unlike"
                console.log("Set to unlike")
            }
            if (!data.liked) {
                $(this).attr('action', 'like')
                document.querySelector(".toggle" + postId).innerHTML = "Like"
                console.log("Set to like")

            }
        })
    })
})
