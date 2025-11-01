import express from 'express';
import panelController from './panel.controller.js';

const router = express.Router();

router.post('/', panelController.handleGetPanel);

export default router;