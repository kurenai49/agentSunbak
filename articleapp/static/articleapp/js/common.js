let bWidth = window.innerWidth;

window.addEventListener("resize", () => {
    const nWidth = window.innerWidth;
    if ((bWidth < 1023 && nWidth >= 1023) || (bWidth > 1023 && nWidth <= 1023)) {
        location.reload();
    }
});



if (bWidth > 1023) {

    // PC

    $('.list_cont .oneline_hover').mouseover(function () {

        // let item = $('.list_cont .oneline_hover')
        let boxs = $('.list_cont .list_item')
        let box = $(this).closest(".list_item")
        let idx = box.index(this);

        boxs.removeClass("hover")
        box.eq(idx).addClass('hover');

    });

    /* 23.07.03 버튼 수정 */

    $(".comment_item > .bnt_dropdown .dropdown_toggle").click(function () {
        $(this).parent().find(".dropdown_menu").addClass("show");
    });

    $(".comment_item > .bnt_dropdown .dropdown-item").click(function () {
        $(".bnt_dropdown .dropdown_menu").removeClass("show");
    });

    $(document).mouseup(function (e) {
        if ($(".bnt_dropdown .dropdown_menu").has(e.target).length === 0) {
            $(".bnt_dropdown .dropdown_menu").removeClass("show");
        }

    });

    // 23.08.12 추가

    $(".oneline_toggle").click(function () {
        let item = $(this).parents(".list_item")
        
        if (item.hasClass("hover")) {
            item.removeClass("hover");
        } else {
            item.addClass("hover");
        }
    });



} else {

    // Tablet && Mobile   

    $(".comment_modal_toggle").click(function () {
        $(".comment_modal_wrap").addClass("show");
        $("body").addClass("hidden");
    });

    $(".comment_modal_clo").click(function () {
        $(".comment_modal_wrap").removeClass("show");
        $("body").removeClass("hidden");
    });

    // $(".bnt_dropdown").click(function () {
    //     $(".comment_modal_btnbox").addClass("show");
    //     $("body").addClass("hidden");
    // });

    // $(".comment_modal_btnbox .btnbox .btn").click(function () {
    //     $(".comment_modal_btnbox").toggleClass("show");
    //     $("body").removeClass("hidden");
    // });


    /* 23.07.03 버튼 수정 */
    $(".comment_item > .bnt_dropdown .dropdown_toggle").click(function () {
        $(this).siblings(".dropdown_menu").addClass("show");
        $("body").addClass("hidden");
    });

    $(".comment_item > .bnt_dropdown .dropdown-item").click(function () {
        $(".dropdown_menu").removeClass("show");
    });


    $(document).mouseup(function (e) {
        if ($(".comment_modal_wrap").has(e.target).length === 0) {

            $(".comment_modal_wrap").removeClass("show");
            $('body').removeClass("hidden");
        }

        if ($(".comment_modal_btnbox .btnbox").has(e.target).length === 0) {

            $(".comment_modal_btnbox").removeClass("show");

        }

        /* 23.07.03 버튼 수정 */

        if ($(".comment_item > .bnt_dropdown .dropdown-item").has(e.target).length === 0) {

            $(".dropdown_menu").removeClass("show");

        }
    });

}


$(document).ready(function () {

    $(".hover_close").click(function () {
        $(".list_cont .list_item").removeClass("hover");
    });


    // 23.08.11 추가 - 마이페이지 버튼
    $(".mypage_btn").click(function () {
        $(".mypage_box").toggleClass("open");
        $(".mypage_popup").toggleClass("show");
    });

    $(".view_wrap .btn-edit").click(function () {
        $(".view_wrap .edit_modal").toggleClass("show");
    });

    $(document).mouseup(function (e) {
        if ($(".mypage_box").has(e.target).length === 0) {
            $(".mypage_box").removeClass("open");
            $(".mypage_popup").removeClass("show");
        }
    });

    $(document).mouseup(function (e) {
        if ($(".view_wrap .edit_modal .btn_item").has(e.target).length === 0) {
            $(".view_wrap .edit_modal").removeClass("show");
        }
    });



});