<template>
     <div v-if="ready" class="uk-card-header uk-card-default uk-card-body uk-card-hover uk-margin-bottom">
            <h3 class="uk-card-title" v-text="title"></h3>
            <p v-text="comment"></p>
        </div>
</template>
<script>
export default {
	  props: ['ready', 'title', 'comment']
}
</script>