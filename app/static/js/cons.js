var field = {
    'astro-ph': 'Astrophysics',
    'cond-mat': 'Condensed Matter',
    'gr-qc': 'General Relativity and Quantum Cosmology',
    'hep-ex': 'High Energy Physics - Experiment',
    'hep-lat': 'High Energy Physics - Lattice',
    'hep-ph': 'High Energy Physics - Phenomenology',
    'hep-th': 'High Energy Physics - Theory',
    'math-ph': 'Mathematical Physics',
    'nlin': 'Nonlinear Sciences',
    'nucl-ex': 'Nuclear Experiment',
    'nucl-th': 'Nuclear Theory',
    'physics': 'Physics',
    'quant-ph': 'Quantum Physics',
    'math': 'Mathematics',
    'CoRR': 'Computing Research Repository',
    'q-bio': 'Quantitative Biology',
    'q-fin': 'Quantitative Finance',
    'stat': 'Statistics',
    'eess': 'Electrical Engineering and System Science',
    'econ': 'Economics'
};

//extend jQuery
$(function () {
    $.extend({
        postJSON: function (url, data) {
            var query = $.ajax({
                url: url,
                data: JSON.stringify(data),
                type: "POST",
                dataType: "json",
                contentType: "application/json"
            });
            return query;

        }
    });
});


