import '../../../dist/terra-ui-components.js'
import { expect, fixture, html } from '@open-wc/testing'

describe('<terra-combobox>', () => {
    it('should render a component', async () => {
        const el = await fixture(html` <terra-combobox></terra-combobox> `)

        expect(el).to.exist
    })
})
