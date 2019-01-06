Vue.component('navBar', {
    props: ['islogin', 'name'],
    methods: {
        logout: function (event) {
            event.preventDefault();
            var lo = $.getJSON("/api/logout");
            lo.done(function () {
                window.location.href = "/login";
            });
        }
    },
    template: `
<nav class="uk-navbar-container" style="height:50px" uk-navbar>
    <div class="uk-navbar-left">
        <ul class="uk-navbar-nav">
        <li class="uk-margin-left"><a href="/">Home</a></li>
        </ul>
    </div>
    <div class="uk-navbar-right">
        <ul class="uk-navbar-nav">
        
                <li v-if="islogin" class="uk-margin-right"><a href="#" v-text="name"></a>
                    <div class="uk-navbar-dropdown">
                        <ul class="uk-nav uk-navbar-dropdown-nav">
                            <li><a href="/settings/keywords">Edit Keywords</a></li>
                            <li><a href="/settings/userinfo">Edit Profiles</a></li>
                            <hr>
                            <li><a href="/api/logout" v-on:click="logout">Log Out</a></li>
                        </ul>
                    </div>
                </li>


                <li v-else class="uk-margin-right"><a class="uk-logo" href="/login">Log In</a>
                    <div class="uk-navbar-dropdown">
                        <ul class="uk-nav uk-navbar-dropdown-nav">
                            <li><a href="/register">Sign Up</a></li>
    
                        </ul>
                    </div>
                </li>

        </ul>
    </div>
</nav>
    `
});

Vue.component('paginate', {
    props: ['hasprev', 'hasnext', 'page', 'last'],

    methods: {
        changepage: function (num, event) {
            event.preventDefault();
            this.$emit('gopage', num);
        }
    },
    template: `
<div class="uk-margin-top">
<ul class="uk-pagination">
    <li v-if="hasprev" class="uk-margin-auto-right"><a href="" v-on:click="changepage(-1, $event)"><span class="uk-margin-small-right" uk-pagination-previous></span> Previous</a></li>
    <li v-else class="uk-margin-auto-right"><span class="uk-margin-small-left uk-disabled"></span> </li>

    <li class="uk-margin-auto-left uk-margin-auto-right"><a href="" uk-scroll v-text=" 'ToTop (Page '+page+'/'+last+')' "></a></li>
    
    <li v-if="hasnext" class="uk-margin-auto-left" ><a href="" v-on:click="changepage(1, $event)">Next<span class="uk-margin-small-left" uk-pagination-next></span></a></li>
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
});

Vue.component('refreshBoard', {
    props: ['ready', 'title', 'comment'],
    template: `
     <div v-if="ready" class="uk-card-header uk-card-default uk-card-body uk-card-hover uk-margin-bottom">
            <h3 class="uk-card-title" v-text="title"></h3>
            <p v-text="comment"></p>
        </div>
    `
});