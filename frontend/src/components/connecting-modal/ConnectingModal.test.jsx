import { render, screen } from '@testing-library/react'
import ConnectingModal from './ConnectingModal.jsx'
import { describe, it, expect } from 'vitest'

describe('ConnectingModal', () => {
  it('should show when the show property is set', () => {
    render(<ConnectingModal show={true} />)

    expect(screen.queryByText('Connecting to backend')).toBeInTheDocument()
  })

  it('should not show when the show property is not set', () => {
    render(<ConnectingModal show={false} />)

    expect(screen.queryByText('Connecting to backend')).not.toBeInTheDocument()
  })
})
