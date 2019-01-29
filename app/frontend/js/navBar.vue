<template>
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
</template>
<script>
export default {
	props: ['islogin', 'name'],
    methods: {
        logout: function (event) {
            event.preventDefault();
            var lo = $.getJSON("/api/logout");
            lo.done(function () {
                window.location.href = "/login";
            });
        }
    }
}
</script>