<script setup>
defineProps({
    endpoint: { type: String, default: "" },
    note: { type: String, default: "" },
});

</script>

<template>
    <div v-if="endpoint || note"
        class="mt-3 rounded-xl border border-green-100 bg-green-50/60 px-3 py-2 text-xs text-green-800">
        <div v-if="endpoint"><strong>API:</strong> {{ endpoint }}</div>
        <div v-if="note" class="mt-0.5 text-green-700">{{ note }}</div>
    </div>
</template>
