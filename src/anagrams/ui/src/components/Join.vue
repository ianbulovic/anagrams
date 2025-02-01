<script setup>

const props = defineProps({
    ws: WebSocket
})

const join = function () {
    var playerName = document.getElementById("joinPlayerNameInput").value;
    var gameId = document.getElementById("gameIdInput").value;
    props.ws?.send(JSON.stringify({ action: "join", name: playerName, game_id: gameId }));
}

const start = function () {
    var playerName = document.getElementById("startPlayerNameInput").value;
    props.ws?.send(JSON.stringify({ action: "start", name: playerName }));
}
const audioFail = new Audio("/play/sounds/fail.mp3");
const inputFail = function (eid, reason) {
    const failDesc = document.getElementById(eid);

    audioFail.play();
    failDesc.innerText = reason;
    setTimeout(() => { failDesc.classList.remove("wiggle"); }, 300);
    setTimeout(() => { failDesc.innerText = ""; }, 1000);
}

const handleErr = function (message) {
    const err_type = message["err_type"];
    const err_desc = message["description"];

    if (err_type === "join_fail") {
        inputFail("joinErrDesc", err_desc);
    }
    else if (err_type == "start_fail") {
        inputFail("startErrDesc", err_desc);
    }
}

defineExpose({ handleErr });
</script>

<template>
    <div class="flex sm:flex-row gap-20 flex-col mt-10">
        <div class="flex flex-col gap-2 items-center">
            <h2 class="text-3xl lg:text-4xl text-center">Join a Game</h2>
            <input id="joinPlayerNameInput" class="text-lg lg:text-2xl" autocomplete="off" placeholder="Your name" />
            <input id="gameIdInput" class="text-lg lg:text-2xl uppercase placeholder:normal-case" autocomplete="off"
                placeholder="Game ID" />
            <button id="join-button" class="w-full" @click="join(e)">JOIN!</button>
            <span id="joinErrDesc" class="mb-2 text-xl text-red-500"></span>
        </div>
        <div class="flex flex-col gap-2 items-center">
            <h2 class="text-3xl lg:text-4xl text-center">Start a Game</h2>
            <input id="startPlayerNameInput" class="text-lg lg:text-2xl" autocomplete="off" placeholder="Your name" />
            <button id="start-button" class="w-full" @click="start(e)">START!</button>
            <span id="startErrDesc" class="mb-2 text-xl text-red-500"></span>
        </div>
    </div>
</template>

<style scoped></style>
