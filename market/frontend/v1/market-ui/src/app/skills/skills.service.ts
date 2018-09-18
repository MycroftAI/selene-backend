import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';

export class Skill {
    id: number;
    credits: Object;
    categories: string[];
    description: string;
    icon: Object;
    icon_image: string;
    skill_name: string;
    title: string;
    summary: string;
    repository_url: string;
    triggers: string;
}

@Injectable()
export class SkillsService {
    private installUrl = '/api/install-skill';
    private skillUrl = '/api/skill/';
    private skillsUrl = '/api/skills';
    private searchQuery = '?search=';

    constructor(private http: HttpClient) { }

    getAllSkills(): Observable<Skill[]> {
        return this.http.get<Skill[]>(this.skillsUrl)
    }

    getSkillById(id: string): Observable<Skill> {
        return this.http.get<Skill>(this.skillUrl + id)
    }

    searchSkills(searchTerm: string): Observable<Skill[]> {
        return this.http.get<Skill[]>(this.skillsUrl + this.searchQuery + searchTerm)
    }

    installSkill(skill: Skill): Observable<Object> {
        return this.http.put<Object>(
            this.installUrl,
            {skill_url: skill.repository_url}
        )

    }
}
