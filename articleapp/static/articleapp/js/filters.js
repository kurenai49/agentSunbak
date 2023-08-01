function submitForm() {
    document.getElementById('search-form').submit();
}

document.querySelector('.searchbtn').addEventListener('click', function(e) {
    e.preventDefault(); // 기본 폼 제출 방지

    let url = new URL(window.location.href);

    url.searchParams.set('min_modelYear', document.querySelector('#min_modelYear').value);
    url.searchParams.set('max_modelYear', document.querySelector('#max_modelYear').value);

    window.location.href = url.href;
});

$(document).ready(function () {

    function getParameterByName(name) {
        var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
        return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
    }

    var min_price = getParameterByName('min_price') || 0;
    var max_price = getParameterByName('max_price') || 70;
    var min_tons = getParameterByName('min_tons') || 0;
    var max_tons = getParameterByName('max_tons') || 50;

    $("#price").ionRangeSlider({
        type: "double",
        grid: true,
        min: 0,
        max: 70,
        from: min_price,
        to: max_price,
        postfix: " 억원",
        onFinish: function (data) {
            let url = new URL(window.location.href);

            url.searchParams.set('min_price', data.from);
            url.searchParams.set('max_price', data.to);

            window.location.href = url.href;
        },
    });

    $("#tons_weight").ionRangeSlider({
        type: "double",
        grid: true,
        min: 0,
        max: 50,
        from: min_tons,
        to: max_tons,
        postfix: " 톤",
        onFinish: function (data) {

            let url = new URL(window.location.href);

            url.searchParams.set('min_tons', data.from);
            url.searchParams.set('max_tons', data.to);

            window.location.href = url.href;
        },
    });
});
