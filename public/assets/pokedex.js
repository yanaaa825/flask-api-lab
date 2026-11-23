"use strict";

const search = document.querySelector("#search");
const query = document.querySelector("#query");
const status = document.querySelector("#status");
const card = document.querySelector("#card");
const art = document.querySelector("#art");
const imageMessage = document.querySelector("#image-message");
const navigation = document.querySelector("#navigation");
const previous = document.querySelector("#previous");
const next = document.querySelector("#next");
const lastId = Number(document.body.dataset.lastId);
const typeNames = {
    normal: "一般", fire: "火", water: "水", electric: "電", grass: "草",
    ice: "冰", fighting: "格鬥", poison: "毒", ground: "地面", flying: "飛行",
    psychic: "超能力", bug: "蟲", rock: "岩石", ghost: "幽靈", dragon: "龍",
    dark: "惡", steel: "鋼", fairy: "妖精", stellar: "星晶", unknown: "未知"
};

let currentId = null;
let activeRequest;

function setStatus(message, isError = false) {
    status.textContent = message;
    status.classList.toggle("error", isError);
}

function showImage(pokemon) {
    art.querySelector("img")?.remove();
    imageMessage.textContent = "目前沒有可顯示的圖片。";
    imageMessage.hidden = Boolean(pokemon.image_url);
    if (!pokemon.image_url) return;

    const image = document.createElement("img");
    image.alt = (pokemon.name_zh_hant ?? pokemon.name) + " 的圖片";
    image.addEventListener("error", () => {
        if (!art.contains(image)) return;
        image.remove();
        imageMessage.textContent = "圖片載入失敗。";
        imageMessage.hidden = false;
    }, { once: true });
    art.prepend(image);
    image.src = pokemon.image_url;
}

function render(pokemon) {
    document.querySelector("#pokemon-id").textContent = "#" + String(pokemon.id).padStart(4, "0");
    document.querySelector("#pokemon-name").textContent = pokemon.name_zh_hant ?? pokemon.name;
    document.querySelector("#height").textContent = pokemon.height_m + " 公尺";
    document.querySelector("#weight").textContent = pokemon.weight_kg + " 公斤";

    const tags = pokemon.types.map((type) => {
        const tag = document.createElement("li");
        tag.dataset.type = type;
        tag.textContent = Object.hasOwn(typeNames, type) ? typeNames[type] : type;
        return tag;
    });
    document.querySelector("#types").replaceChildren(...tags);
    showImage(pokemon);

    currentId = pokemon.id;
    previous.disabled = currentId <= 1;
    next.disabled = currentId >= lastId;
    navigation.hidden = currentId > lastId;
    card.hidden = false;
}

async function loadPokemon(value) {
    activeRequest?.abort();
    const request = new AbortController();
    activeRequest = request;
    setStatus("載入中…");
    try {
        const response = await fetch("/api/pokemon?" + new URLSearchParams({ q: value }), {
            signal: request.signal,
            headers: { Accept: "application/json" }
        });
        const data = await response.json();
        if (activeRequest !== request) return;
        if (!response.ok) {
            setStatus(typeof data.error === "string" ? data.error : "搜尋失敗，請稍後重試。", true);
            return;
        }
        render(data);
        setStatus("已顯示 " + (data.name_zh_hant ?? data.name) + " 的圖鑑資料。");
    } catch (error) {
        if (activeRequest === request && error.name !== "AbortError") {
            setStatus("暫時無法載入圖鑑資料，請稍後重試。", true);
        }
    }
}

search.addEventListener("submit", (event) => {
    event.preventDefault();
    const value = query.value.trim().normalize("NFKC");
    if (!value || /[/\\]/.test(value) || /^0+$/.test(value)) {
        activeRequest?.abort();
        activeRequest = null;
        setStatus("請輸入繁體中文名稱、英文名稱或正整數圖鑑編號。", true);
        query.focus();
        return;
    }
    loadPokemon(value);
});

document.querySelector("#random").addEventListener("click", () => {
    let id = 1 + Math.floor(Math.random() * (lastId - 1));
    if (currentId === null || currentId > lastId) {
        id = 1 + Math.floor(Math.random() * lastId);
    } else if (id >= currentId) {
        id += 1;
    }
    loadPokemon(id);
});
previous.addEventListener("click", () => loadPokemon(currentId - 1));
next.addEventListener("click", () => loadPokemon(currentId + 1));
loadPokemon(25);
