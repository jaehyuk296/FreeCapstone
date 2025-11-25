import express from 'express';
import compareController from './compare.controller.js';

const router = express.Router();

router.post('/', compareController.handleCompare);

export default router;