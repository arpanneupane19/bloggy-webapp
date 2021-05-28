var modalBtn = document.querySelector('.view-followers');
var modalBg = document.querySelector('.followers-modal');
var closeBtn = document.querySelector('.close-modal');
var modal = document.querySelector('.modal');

if (modalBtn) {
    modalBtn.addEventListener('click', function () {
        modalBg.classList.add('bg-active');
    });
}

closeBtn.addEventListener('click', function () {
    modalBg.classList.remove('bg-active')
})

// return number of likes on post
function likes(total) {
    if (total === 1) {
        return `${total} like`
    }

    if (total > 1 || total === 0) {
        return `${total} likes`
    }
}

// return number of followers on user profile
function followers(total) {
    if (total === 1) {
        return `${total} follower`
    }

    if (total > 1 || total === 0) {
        return `${total} followers`
    }

}

function navigateToPage(path) {
    return window.location.assign(path)
}

$(document).ready(() => {
    // Like posts without reloading.
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

    // Follow users without reloading.
    $(".follow-actions").on("click", function () {
        var username = $(this).attr('username')
        var followAction = $(this).attr('action')
        req = $.ajax({
            url: `/${followAction}/user/${username}`,
            type: 'POST',
            data: { username: username, followAction: followAction }
        })

        req.done((data) => {
            document.querySelector(`.view-followers`).innerHTML = followers(data.total_followers)
            var followersTotal = document.querySelector('.view-followers')
            if (data.total_followers === 1 || data.total_followers > 1) {
                followersTotal.style.color = 'rgb(0,140,255)'
                followersTotal.style.cursor = 'pointer'
            }
            else {
                followersTotal.style.color = '#000'
                followersTotal.style.cursor = 'auto'
            }
            if (data.following) {
                $(this).attr('action', 'unfollow')
                document.querySelector(".follow-unfollow" + username).innerHTML = "Unfollow"
                console.log("Set to unfollow")
            }
            if (!data.following) {
                $(this).attr('action', 'follow')
                document.querySelector(".follow-unfollow" + username).innerHTML = "Follow"
                console.log("Set to follow")
            }

        })
    })
})

