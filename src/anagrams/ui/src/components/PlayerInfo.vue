<script setup>

const props = defineProps({ player: Object, index: Number, kickPlayer: Function });
const player = props.player;
const index = props.index;

</script>
<template>
    <div class="relative">
        <div class="bg-amber-400 text-slate-800 border-4 border-amber-800 p-3 font-black rounded-xl flex flex-col items-center"
            :style="`filter: brightness(80%) hue-rotate(${(index + 1) * 140}deg);`">
            <h1 class="text-xl lg:text-3xl">
                {{ player.name }}
            </h1>
            <p class="text-xs lg:text-sm">
                {{ player.score }} points
            </p>
        </div>
        <span v-if="kickPlayer" @click="kickPlayer(index)"
            class="font-sans bg-red-600 text-slate-800 font-black text-md absolute top-[-5%] right-[-5%] rounded-full w-7 h-7 text-center border-2 border-red-900 hover:bg-red-500">
            ✕
        </span>
    </div>
</template>

<style scoped></style>