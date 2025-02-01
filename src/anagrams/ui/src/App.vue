<script setup>
import { ref } from 'vue';
import Join from './components/Join.vue'
import Game from './components/Game.vue'
import Letter from './components/Letter.vue';
import { useCookie } from 'vue-cookie-next'
const { setCookie, removeCookie } = useCookie()
const ws_host = import.meta.env.DEV ? window.location.host.split(":")[0] + ":8000" : window.location.host;
var ws = new WebSocket(`ws://${ws_host}/ws`);
const gameState = ref(null);
const joinRef = ref(null);
const gameRef = ref(null);
const audioJoinGame = new Audio("/play/sounds/join_game.mp3");
const audioLeaveGame = new Audio("/play/sounds/leave_game.mp3");

ws.onmessage = function (event) {
    const message = JSON.parse(event.data);
    const action = message.action;
    if (action === "set_cookie") {
        setCookie(message["name"], message["value"]);
    } else if (action === "game_state") {
        if (gameState.value === null) {
            audioJoinGame.play();
        }
        gameState.value = message;
    } else if (action === "error") {
        if (message.err_type === "join_fail" || message.err_type === "start_fail") {
            joinRef.value?.handleErr(message);
        } else {
            gameRef.value?.handleErr(message);
        }
    } else if (action === "leave_game") {
        gameState.value = null;
        audioLeaveGame.play();
    }
}
</script>

<template>
    <div class="flex flex-col items-center px-1 md:px-5 overflow-hidden h-full mt-1">
        <h1 class="p-2 md:p-5 flex flex-row gap-4">
            <template v-for="letter in 'ANAGRAMS'">
                <Letter :letter="letter" />
            </template>
        </h1>
        <h2 v-if="gameState !== null" class="text-xl md:text-2xl lg:text-3xl text-amber-800 mb-4">Game code: <span
                class="text-amber-600">{{ gameState.game_id }}</span></h2>
        <hr class=" border-slate-700 w-2xl mb-5" />

        <Join v-if="gameState === null" :ws="ws" ref="joinRef" />
        <Game v-else :ws="ws" :state="gameState" ref="gameRef" />
    </div>
</template>

<style scoped></style>
