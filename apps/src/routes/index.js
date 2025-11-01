import express from 'express';
import panelRouter from '../modules/panels/panel.route.js';
const router = express.Router()

router.use('/panels', panelRouter);

export default router