var tags = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url: '/suggest?movie_id=%QUERY',
        wildcard: '%QUERY',
        filter: function (response) {
            if (!response.status) {
                return
            }

            return $.map(response.movies, function (movie) {
                return movie;
            });
        }
    }
});


$("#selector").typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
        name: 'movies',
        display: 'text',
        source: tags,
        limit: 100,
        templates: {
            empty: 'no any records',
            suggestion: function (data) {
                return '<div><div>' + data.text + '</div><div class="gray">' + data.value + '</div></div>';
            },
        },
    }
).bind('typeahead:select', function (ev, suggestion) {
    window.location.href = `/recommendations/${suggestion.id.toString()}`;
    ev.preventDefault();
});


$('.empty-heart').click(function () {
    $(this).toggleClass('filled-heart');

    const userId = $(this).attr('data-id');
    const titleId = $(this).attr('data-movie');
    const className = $(this).attr('class');

    if (className.indexOf('filled-heart') > -1) {
        $.ajax({
            url: '/user/save',
            data: {
                'user_id': userId,
                'title_id': titleId,
            }
        })
    } else {
        $.ajax({
            url: '/user/remove',
            data: {
                'user_id': userId,
                'title_id': titleId,
            }
        })
    }
});