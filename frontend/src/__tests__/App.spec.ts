import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import ui from '@nuxt/ui/vue-plugin'
import { createRouter, createMemoryHistory } from 'vue-router'

import App from '../App.vue'

describe('App', () => {
  it('renders RouterView', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div />' } }],
    })

    const wrapper = mount(App, {
      global: {
        plugins: [router, ui],
      },
    })

    expect(wrapper.findComponent({ name: 'RouterView' }).exists()).toBe(true)
  })
})
