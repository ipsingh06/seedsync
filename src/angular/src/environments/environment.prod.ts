import {LoggerService} from "../app/services/utils/logger.service"

export const environment = {
    production: true,
    logger: {
        level: LoggerService.Level.WARN
    }
};
