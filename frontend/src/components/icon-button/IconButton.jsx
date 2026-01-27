import Button from 'react-bootstrap/Button'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './IconButton.css'

/**
 * A bootstrap `Button` with a FontAwesome icon inserted to the left (or right) of the button contents.
 *
 * @param {*|undefined} icon If set, this icon is inserted to the left of the button contents.
 * @param {*|undefined} iconRight If set, this icon is inserted to the right of the button contents.
 * @param {JSX.Element} children Child elements.
 * @param props Other props for the Bootstrap `Button` component.
 * @returns {JSX.Element}
 * @component
 */
export default function IconButton({ icon, iconRight, children, ...props }) {
  return (
    <Button {...props}>
      {icon && <FontAwesomeIcon icon={icon} className="btn-icon" />}
      {children}
      {iconRight && <FontAwesomeIcon icon={iconRight} className="btn-icon-right" />}
    </Button>
  )
}
