<script setup>

import Letter from './Letter.vue';

const props = defineProps({ word: String });

</script>

<template>
    <div class="flex flex-row flex-nowrap gap-1">
        <Letter v-for="letter in word" :letter="letter" />
    </div>
</template>

<style scoped></style>
