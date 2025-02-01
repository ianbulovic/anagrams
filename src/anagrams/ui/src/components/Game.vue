<script setup>
import { watch } from 'vue';
import Letter from './Letter.vue';
import Word from './Word.vue';
import PlayerInfo from './PlayerInfo.vue';

// import failSound from "/sounds/fail.ogg";

const props = defineProps({
    ws: WebSocket,
    state: Object,
})

const audioFail = new Audio("/play/sounds/fail.mp3");
const audioMakeWord = new Audio("/play/sounds/make_word.mp3");
const audioNewLetter = new Audio("/play/sounds/new_letter.mp3");
const audioOpponentMakeWord = new Audio("/play/sounds/opponent_make_word.mp3");
const audioMyWordStolen = new Audio("/play/sounds/my_word_stolen.mp3");
const audioYourTurn = new Audio("/play/sounds/your_turn.mp3");

const playerOne = props.state?.players[0].you;

const me = function (state) {
    return state?.players.find((player) => player.you)
}

const isMyTurn = function (state) {
    return state?.players.find((player) => player.turn && player.you) !== undefined;
}

watch(() => props.state, (cur, prev) => {
    if (isMyTurn(cur) && !isMyTurn(prev)) {
        // It's my turn now (and it wasn't before)
        audioYourTurn.play();
        const newLetterButton = document.getElementById("newLetterButton");
        newLetterButton.classList.add("bulge");
        setTimeout(() => { newLetterButton.classList.remove("bulge"); }, 300);
    } else if (cur.letter_pool.length > prev.letter_pool.length) {
        // A new letter appeared
        audioNewLetter.play();
    }
    if (
        me(cur)?.score > me(prev)?.score || (  // my score went up
            me(cur)?.score === me(prev)?.score &&           // my score didn't change but I have fewer words
            me(cur)?.words.length < me(prev)?.words.length) // (I combined my own words to a make a new word)
    ) {
        // I made a word!
        audioMakeWord.play();
    } else if (me(cur)?.score < me(prev)?.score) {
        // Someone stole my word! :(
        audioMyWordStolen.play();
    } else if (
        cur.players.reduce((p, c) => p + c.score, 0)
        > prev.players.reduce((p, c) => p + c.score, 0)
    ) {
        // Someone made a word
        audioOpponentMakeWord.play();
    }

});

const nextLetter = function (e) {
    if (!('ontouchstart' in document.documentElement)) {
        const inputBox = document.getElementById("wordInput");
        inputBox.focus();
    }
    props.ws?.send(JSON.stringify({ action: "letter" }));
}

var errDescTimeout = null;
const inputFail = function (reason) {
    const inputBox = document.getElementById("wordInput");
    const inputErrDesc = document.getElementById("inputErrDesc");
    inputBox.classList.add("wiggle");
    audioFail.play();
    inputErrDesc.innerText = reason;
    clearTimeout(errDescTimeout);
    setTimeout(() => { inputBox.classList.remove("wiggle"); }, 300);
    errDescTimeout = setTimeout(() => { inputErrDesc.innerText = ""; }, 1000);
}

const submitWord = function (e) {
    const inputBox = document.getElementById("wordInput");
    inputBox.value = inputBox.value.trim();
    const word = inputBox.value;
    if (word.length === 0) {
        return
    } else if (/^[a-zA-Z]{3,}$/.test(word)) {
        inputBox.value = "";
        props.ws?.send(JSON.stringify({ action: "word", word: word }));
    } else if (word.length < 3) {
        inputFail("Too short!");
    } else {
        inputFail("Invalid word!");
    }
}
const kickPlayer = function (playerIndex) {
    props.ws?.send(JSON.stringify({ action: "kick", player_index: playerIndex }));
}

const handleErr = function (message) {
    const err_type = message["err_type"];
    const err_desc = message["description"];

    if (err_type === "unknown_word" || err_type == "unconstructable_word") {
        inputFail(err_desc);
    }
}



defineExpose({ handleErr });

</script>

<template>

    <div class="flex flex-row gap-4 md:gap-6 lg:gap-8 flex-wrap justify-center w-full px-5 md:px-10 lg:px-20 mb-10">
        <template v-for="(letter, index) in state.letter_pool">
            <Letter :letter="letter" :class="{ bulge: index === (state.letter_pool.length - 1) }" />
        </template>
    </div>
    <div class="grow" style="flex: auto; flex-grow: 1; overflow: scroll;">
        <div class="flex flex-row flex-wrap justify-center w-full gap-3 px-5 md:gap-4 md:px-10 lg:gap-5 lg:px-15">
            <template v-for="(player, index) in state.players">
                <template v-for="word in player.words">
                    <Word :word="word" class="brightness-50"
                        :style="`filter: brightness(80%) hue-rotate(${(index + 1) * 140}deg);`" />
                </template>
            </template>
        </div>
    </div>

    <div class="xl:grid grid-rows-1 grid-cols-3 w-full mb-3">

        <!-- First half of player list -->
        <div class="xl:flex flex-row gap-10 w-full justify-around my-3 hidden">
            <template v-for="(player, index) in state.players">
                <PlayerInfo v-if="index < state.players.length / 2" :player="player" :index="index"
                    :kickPlayer="playerOne ? kickPlayer : undefined" />
            </template>
        </div>

        <!-- Word input and new letter button -->
        <div class="flex flex-col items-center">
            <div class="flex flex-col items-center flex-initial">
                <span id="inputErrDesc" class="mb-2 text-xl text-red-500"></span>
                <input id="wordInput" type="text" autofocus class="w-xs text-xl lg:w-md lg:text-4xl"
                    placeholder="Enter a word..." @keyup.enter="submitWord" autocomplete="off" autocorrect="off"
                    autocapitalize="off" spellcheck="false" />
            </div>
            <button id="newLetterButton" class="my-3" @click="nextLetter" :disabled="!isMyTurn(props.state)">
                New Letter
            </button>
        </div>

        <!-- Second half of player list -->
        <div class="xl:flex flex-row gap-10 w-full justify-around my-3 hidden">
            <template v-for="(player, index) in state.players">
                <PlayerInfo v-if="index >= state.players.length / 2" :player="player" :index="index"
                    :kickPlayer="playerOne ? kickPlayer : undefined" />
            </template>
        </div>
    </div>
    <!-- Second half of player list -->
    <div class="flex flex-row gap-10 w-full justify-around mb-6 xl:hidden">
        <template v-for="(player, index) in state.players">
            <PlayerInfo :player="player" :index="index" :kickPlayer="playerOne ? kickPlayer : undefined" />
        </template>
    </div>

</template>

<style scoped></style>
