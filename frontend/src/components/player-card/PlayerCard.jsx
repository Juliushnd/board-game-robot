import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import './PlayerCard.css'

/**
 * A card displaying a player's icon and name.
 *
 * @param {String} name The player's name.
 * @param {*} icon The player's icon.
 * @returns {JSX.Element}
 * @component
 */
export default function PlayerCard({ name, icon }) {
  return (
    <div className="player-card">
      <FontAwesomeIcon icon={icon} className="player-icon" />
      {name}
    </div>
  )
}
