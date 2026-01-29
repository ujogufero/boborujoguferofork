<script setup>
import { ref, onMounted } from "vue";

const data = ref(null);
const error = ref(null);
const loading = ref(true);

const fetchData = async () => {
    try {
        const response = await fetch("/api");
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        data.value = await response.json();
    } catch (err) {
        error.value = err.message;
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchData();
});
</script>

<template>
    <div class="container">
        <div v-if="loading" class="status">Loading...</div>
        <div v-else-if="error" class="status error">Error: {{ error }}</div>
        <div v-else class="data-container">
            <pre>{{ JSON.stringify(data, null, 2) }}</pre>
        </div>

        <button @click="fetchData" :disabled="loading">
            {{ loading ? "Updating..." : "Refresh" }}
        </button>
    </div>
</template>

<style scoped>
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    font-family:
        "Inter",
        system-ui,
        -apple-system,
        sans-serif;
    text-align: center;
}

h1 {
    font-size: 3rem;
    margin-bottom: 2rem;
    background: linear-gradient(135deg, #646cff 0%, #42b883 100%);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.data-container {
    background: #1a1a1a;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: left;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    border: 1px solid #333;
}

pre {
    margin: 0;
    color: #42b883;
    font-family: "Fira Code", "Courier New", monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
}

button {
    padding: 0.8rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: white;
    background: #646cff;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover:not(:disabled) {
    background: #535bf2;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(100, 108, 255, 0.3);
}

button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.status {
    margin: 1rem 0;
    font-size: 1.2rem;
}

.error {
    color: #ff4444;
}
</style>
