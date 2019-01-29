<template>
 <div id="warning" v-if="seen" class="uk-margin-top"
         v-bind:class="{'uk-alert-success': issuccess, 'uk-alert-warning': ! issuccess}" uk-alert>
        <a class="uk-alert-close" uk-close v-on:click="hide"></a>
        <p v-text="message"></p>
    </div>
</template>
<script>
export default {
	props: ['issuccess', 'message', 'seen'],
    methods: {
        hide: function (event) {
            event.preventDefault();
            this.$emit('update:seen', false)
        }
    }
}
</script>
