// @ts-check

/**
 * @typedef {Object} Message
 * @property {string} id
 * @property {string} session_id
 * @property {string} sender_id
 * @property {"text"|"image"|"video"|"audio"|"system-recall"|"system-time"|"system-hint"|"system-emotion"|"system-typing"} type
 * @property {string} content
 * @property {Record<string, any>} metadata
 * @property {boolean} is_recalled
 * @property {boolean} is_read
 * @property {number} timestamp
 */

/**
 * @typedef {Object} Character
 * @property {string} id
 * @property {string} name
 * @property {string} avatar
 * @property {string} persona
 * @property {boolean} is_builtin
 */

/**
 * @typedef {Object} Session
 * @property {string} id
 * @property {string} character_id
 * @property {boolean} is_active
 */

/**
 * @typedef {Object} WsEvent
 * @property {string} type
 * @property {any} data
 */

