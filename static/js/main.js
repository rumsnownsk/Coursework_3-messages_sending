$(function () {



    $('#search-form-btn').on('click', function (e) {
        e.preventDefault();
        let form = $(this).parent();
        let inputSearch = form.find('.form-control');
        inputSearch.toggleClass('show').focus();
        if (inputSearch.val()) {
            form.submit();
        }
    });

    // $('.counter-num').spincrement();

    let counterBox = $('.achievments');
    if (counterBox.length) {
        let counterItem = $('.counter-num');
        let showCounter = true;

        $(window).on('scroll load resize', function () {
            let counterBoxTop = counterBox.offset().top;
            let windowHeight = window.innerHeight;
            let windowTop = $(window).scrollTop();

            if (showCounter && (counterBoxTop + 200 < windowTop + windowHeight)) {
                showCounter = false;
                counterItem.css('opacity', 1);
                counterItem.spincrement({
                    duration: 2000
                });
                // console.log(counterBoxTop, windowHeight, windowTop);
            }
        });
    }


  

    $(".phone-mask").mask("+3(999) 999-9999");

    const topBtn = $('#top');
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            topBtn.fadeIn();
        } else {
            topBtn.fadeOut();
        }
    });

    topBtn.click(function () {
        $('html, body').animate({scrollTop: 0}, 500);
        return false;
    });

});

function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}

function setCookie(name, value, options = {}) {

    options = {
        path: '/',
        // при необходимости добавьте другие значения по умолчанию
        ...options
    };

    if (options.expires instanceof Date) {
        options.expires = options.expires.toUTCString();
    }

    let updatedCookie = encodeURIComponent(name) + "=" + encodeURIComponent(value);

    for (let optionKey in options) {
        updatedCookie += "; " + optionKey;
        let optionValue = options[optionKey];
        if (optionValue !== true) {
            updatedCookie += "=" + optionValue;
        }
    }

    document.cookie = updatedCookie;
}

function deleteCookie(name) {
    setCookie(name, "", {
        'max-age': -1
    })
}

// Пример использования:
// setCookie('user', 'John', { 'max-age': 10 });
// console.log(getCookie('user'));
const offcanvasCookie = new bootstrap.Offcanvas('#offcanvasCookie');

if (!getCookie('allowCookie')) {
    setTimeout(() => {
        offcanvasCookie.show();
    }, 3000);
}

document.querySelector('#allow-cookie').addEventListener('click', (e) => {
    e.preventDefault();
    setCookie('allowCookie', 1, {'max-age': 3600 * 24 * 365});
    offcanvasCookie.hide();
});
