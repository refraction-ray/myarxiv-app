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

Vue.component('paginate', {
    props: ['hasprev', 'hasnext', 'page'],
    data: function () {
        function param(name) {
            return (location.search.split(name + '=')[1] || '').split('&')[0];
        }

        var page = param("page");
        var date = param("date");
        var keyword = param("keyword");
        var nextpage = (Number(page) + 1).toString();
        var prevpage = (Number(page) - 1).toString();
        var urlbase = window.location.pathname + "?";
        return {
            nexturl: urlbase + $.param({"page": nextpage, "date": date, "keyword": keyword}),
            prevurl: urlbase + $.param({"page": prevpage, "date": date, "keyword": keyword})
        }
    },
    methods: {},
    template: `
<div class="uk-margin-top">
<ul class="uk-pagination">
    <li v-if="hasprev" class="uk-margin-auto-right"><a :href="prevurl"><span class="uk-margin-small-right" uk-pagination-previous></span> Previous</a></li>
    <li v-else class="uk-margin-auto-right"><span class="uk-margin-small-left uk-disabled"></span> </li>

    <li class="uk-margin-auto-left uk-margin-auto-right"><a href="#" uk-scroll>ToTop</a></li>
    <li v-if="hasnext" class="uk-margin-auto-left" ><a :href="nexturl">Next<span class="uk-margin-small-left" uk-pagination-next></span></a></li>
    <li v-else class="uk-margin-auto-left"><span class="uk-margin-small-right uk-disabled"></span> </li>

</ul>
</div>
`

});

Vue.component('flash', {
    props: ['issuccess', 'message', 'seen'],
    methods: {
        hide: function (event) {
            event.preventDefault();
            this.$emit('update:seen', false)
        }
    },

    template: `
    <div id="warning" v-if="seen" class="uk-margin-top"
         v-bind:class="{'uk-alert-success': issuccess, 'uk-alert-warning': ! issuccess}" uk-alert>
        <a class="uk-alert-close" uk-close v-on:click="hide"></a>
        <p v-text="message"></p>
    </div>
    `
})