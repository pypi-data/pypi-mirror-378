import '../../../dist/terra-ui-components.js'
import { expect, fixture, html } from '@open-wc/testing'

describe('<terra-data-rods>', () => {
    it('should render a component', async () => {
        const el = await fixture(html` <terra-data-rods></terra-data-rods> `)

        expect(el).to.exist
    })
})
