// Generated from contracts/api/v1/openapi.json. Run npm run contracts:generate.
export interface paths {
    "/api/v1/health/live": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Liveness */
        get: operations["getLiveness"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/health/ready": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Readiness */
        get: operations["getReadiness"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/programs": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * List Programs
         * @description Browse the catalogue of published learning programs.
         */
        get: operations["list_programs_api_v1_programs_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/programs/{slug}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /**
         * Get Program
         * @description Fetch complete details of a published program by its unique URL slug.
         */
        get: operations["get_program_api_v1_programs__slug__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/programs/{slug}/applications": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /**
         * Submit Application
         * @description Submit an unverified enrolment application for a published program.
         */
        post: operations["submit_application_api_v1_programs__slug__applications_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /**
         * ApplicationReceiptResponse
         * @description Minimal receipt returned to the guardian after submission.
         *
         *     Excludes personal data from replay-query output in accordance with
         *     least-privilege database permissions.
         */
        ApplicationReceiptResponse: {
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /**
             * Is Retry
             * @description True if this response was returned from an earlier identical submission.
             */
            is_retry: boolean;
            /**
             * Program Id
             * Format: uuid
             */
            program_id: string;
            /**
             * Reference
             * @description Unique, human-friendly application tracking reference.
             */
            reference: string;
            status: components["schemas"]["ApplicationStatus"];
            /**
             * Submitted At
             * Format: date-time
             */
            submitted_at: string;
        };
        /**
         * ApplicationStatus
         * @description Lifecycle of an enrolment application.
         *
         *     Applications start as 'submitted' and move through review.
         *     An application must not automatically create an approved enrolment.
         * @enum {string}
         */
        ApplicationStatus: "submitted" | "under_review" | "approved" | "rejected" | "withdrawn";
        /**
         * GuardianRelationship
         * @description The applicant's relationship to the learner.
         * @enum {string}
         */
        GuardianRelationship: "parent" | "guardian" | "grandparent" | "sibling" | "other";
        /** LivenessResponse */
        LivenessResponse: {
            /**
             * Service
             * @default jjenga-lms-api
             * @constant
             */
            service: "jjenga-lms-api";
            /**
             * Status
             * @default ok
             * @constant
             */
            status: "ok";
            /**
             * Version
             * @default 0.1.0
             */
            version: string;
        };
        /**
         * Pathway
         * @description The three learning pathway categories offered by Jjenga Code.
         * @enum {string}
         */
        Pathway: "school_term" | "saturday_club" | "holiday";
        /**
         * ProgramDelivery
         * @description How a program is delivered to learners.
         * @enum {string}
         */
        ProgramDelivery: "in_person" | "online" | "hybrid";
        /**
         * ProgramDetailResponse
         * @description Full public details of a published program including rich description.
         */
        ProgramDetailResponse: {
            /** Applications Close At */
            applications_close_at: string | null;
            /** Applications Enabled */
            applications_enabled: boolean;
            /** Applications Open At */
            applications_open_at: string | null;
            delivery: components["schemas"]["ProgramDelivery"];
            /** Description */
            description: string;
            /** Display Order */
            display_order: number;
            /** Ends On */
            ends_on: string | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Max Age Years */
            max_age_years: number | null;
            /** Max Enrolments */
            max_enrolments: number | null;
            /** Min Age Years */
            min_age_years: number | null;
            pathway: components["schemas"]["Pathway"];
            /**
             * Slug
             * @description URL slug (1-100 lowercase alphanumeric characters with hyphens).
             */
            slug: string;
            /** Starts On */
            starts_on: string | null;
            status: components["schemas"]["ProgramStatus"];
            /** Summary */
            summary: string;
            /** Title */
            title: string;
        };
        /**
         * ProgramListResponse
         * @description Paginated collection of published programs.
         */
        ProgramListResponse: {
            /** Items */
            items: components["schemas"]["ProgramSummaryResponse"][];
            /** Page */
            page: number;
            /** Page Size */
            page_size: number;
            /** Total */
            total: number;
            /** Total Pages */
            total_pages: number;
        };
        /**
         * ProgramStatus
         * @description Publication lifecycle of a program.
         *
         *     Only 'published' programs are visible in public listings.
         * @enum {string}
         */
        ProgramStatus: "draft" | "published" | "archived";
        /**
         * ProgramSummaryResponse
         * @description Brief public overview of a published program.
         */
        ProgramSummaryResponse: {
            /** Applications Close At */
            applications_close_at: string | null;
            /** Applications Enabled */
            applications_enabled: boolean;
            /** Applications Open At */
            applications_open_at: string | null;
            delivery: components["schemas"]["ProgramDelivery"];
            /** Display Order */
            display_order: number;
            /** Ends On */
            ends_on: string | null;
            /**
             * Id
             * Format: uuid
             */
            id: string;
            /** Max Age Years */
            max_age_years: number | null;
            /** Max Enrolments */
            max_enrolments: number | null;
            /** Min Age Years */
            min_age_years: number | null;
            pathway: components["schemas"]["Pathway"];
            /**
             * Slug
             * @description URL slug (1-100 lowercase alphanumeric characters with hyphens).
             */
            slug: string;
            /** Starts On */
            starts_on: string | null;
            status: components["schemas"]["ProgramStatus"];
            /** Summary */
            summary: string;
            /** Title */
            title: string;
        };
        /** ReadinessResponse */
        ReadinessResponse: {
            /**
             * Status
             * @default ready
             * @constant
             */
            status: "ready";
        };
        /**
         * SubmitApplicationRequest
         * @description Applicant payload for submitting an enrolment application.
         *
         *     Unknown properties (for example a client trying to send ``status`` or
         *     ``reviewed_at``) are rejected rather than silently discarded.
         */
        SubmitApplicationRequest: {
            /**
             * Declaration Accepted
             * @description Must be true to acknowledge and accept the applicant declaration.
             */
            declaration_accepted: boolean;
            /**
             * Declaration Version
             * @description Positive version number of the declaration text agreed to.
             * @default 1
             */
            declaration_version: number;
            /**
             * Guardian Email
             * @description Contact email address for application correspondence.
             */
            guardian_email: string;
            /**
             * Guardian Name
             * @description Full name of the parent or guardian.
             */
            guardian_name: string;
            /**
             * Guardian Phone
             * @description Optional contact telephone number.
             */
            guardian_phone?: string | null;
            /** @description Relationship of the applicant to the learner. */
            guardian_relationship: components["schemas"]["GuardianRelationship"];
            /**
             * Idempotency Key
             * Format: uuid
             * @description Client-generated UUID to ensure submission idempotency.
             */
            idempotency_key: string;
            /**
             * Learner Age Years
             * @description Age of the learner in completed years, as a whole number. Program eligibility is checked separately against the program's own age range.
             */
            learner_age_years: number;
            /**
             * Learner Name
             * @description Full name of the learner.
             */
            learner_name: string;
            /**
             * Notes
             * @description Optional additional context or special learning requirements.
             */
            notes?: string | null;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    getLiveness: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["LivenessResponse"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
        };
    };
    getReadiness: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ReadinessResponse"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Database unavailable or unconfigured */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
        };
    };
    list_programs_api_v1_programs_get: {
        parameters: {
            query?: {
                /** @description Filter by learning pathway */
                pathway?: components["schemas"]["Pathway"] | null;
                /** @description Page number for pagination */
                page?: number;
                /** @description Items per page (max 50) */
                page_size?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProgramListResponse"];
                };
            };
            /** @description Not Found */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
        };
    };
    get_program_api_v1_programs__slug__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                slug: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ProgramDetailResponse"];
                };
            };
            /** @description No published program has this slug */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Unprocessable Entity */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Persistence temporarily unavailable; retry rather than assume absence */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
    submit_application_api_v1_programs__slug__applications_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                slug: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SubmitApplicationRequest"];
            };
        };
        responses: {
            /** @description Original receipt returned for safe idempotent replay */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApplicationReceiptResponse"];
                };
            };
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ApplicationReceiptResponse"];
                };
            };
            /** @description Program not found or not published */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Idempotency key reused with different request payload */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Request body exceeds the configured size limit */
            413: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Validation failure, ineligible age or applications closed */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Too many submissions from this connection; see Retry-After */
            429: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
            /** @description Internal Server Error */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/problem+json": {
                        /** Detail */
                        detail: string;
                        /** Errors */
                        errors?: {
                            [key: string]: unknown;
                        }[] | null;
                        /** Instance */
                        instance: string;
                        /** Request Id */
                        request_id: string;
                        /** Status */
                        status: number;
                        /** Title */
                        title: string;
                        /**
                         * Type
                         * @default about:blank
                         */
                        type: string;
                    };
                };
            };
            /** @description Persistence temporarily unavailable; the submission may need a retry */
            503: {
                headers: {
                    [name: string]: unknown;
                };
                content?: never;
            };
        };
    };
}
