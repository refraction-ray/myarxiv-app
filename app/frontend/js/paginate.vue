<template>
    <div class="uk-margin-top">
        <ul class="uk-pagination">
            <li v-if="hasprev" class="uk-margin-auto-right"><a href="" v-on:click="changepage(-1, $event)"><span class="uk-margin-small-right" uk-pagination-previous></span> Previous</a></li>
            <li v-else class="uk-margin-auto-right"><span class="uk-margin-small-left uk-disabled"></span> </li>
            <li class="uk-margin-auto-left uk-margin-auto-right"><a href="" uk-scroll v-text=" 'ToTop (Page '+page+'/'+last+')' "></a></li>
            <li v-if="hasnext" class="uk-margin-auto-left"><a href="" v-on:click="changepage(1, $event)">Next<span class="uk-margin-small-left" uk-pagination-next></span></a></li>
            <li v-else class="uk-margin-auto-left"><span class="uk-margin-small-right uk-disabled"></span> </li>
        </ul>
    </div>
</template>
<script>
export default {
	 props: ['hasprev', 'hasnext', 'page', 'last'],

    methods: {
        changepage: function (num, event) {
            event.preventDefault();
            this.$emit('gopage', num);
        }
    }
}
</script>