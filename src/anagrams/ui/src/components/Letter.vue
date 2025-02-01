<script setup>

const props = defineProps({ letter: String });

</script>

<template>
    <div
        class="letter font-bold uppercase rounded-md text-2xl w-8 h-8 md:text-3xl md:w-10 md:h-10 lg:text-5xl lg:w-13 lg:h-13 flex items-center justify-center bg-amber-300 text-slate-800">
        {{ letter }}
    </div>
</template>

<style scoped>
.letter {
    box-shadow: 1px 3px var(--color-amber-900);
}
</style>
