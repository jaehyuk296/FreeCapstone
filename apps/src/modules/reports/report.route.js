import express from 'express';
import reportController from './report.controller.js';

const router = express.Router();

router.post('/', reportController.handleGetReport);

export default router;