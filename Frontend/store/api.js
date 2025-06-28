import { defineStore } from 'pinia'

export const api = defineStore('apiUrl', {
	state: () => ({
		url: 'http://85.175.100.129:72/',
	}),
})