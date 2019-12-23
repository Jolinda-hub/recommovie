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
    window.location.href = `/recommendations/${suggestion.id.toString()}/${suggestion.text}`;
    ev.preventDefault();
});