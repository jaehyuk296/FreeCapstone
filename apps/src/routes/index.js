import express from 'express';
import panelRouter from '../modules/panels/panel.route.js';
import reportRouter from '../modules/reports/report.route.js';
const router = express.Router()

router.use('/panels', panelRouter);
router.use('/reports', reportRouter);

export default router